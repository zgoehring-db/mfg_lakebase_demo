import streamlit as st
import psycopg
import os
import time
import uuid
import re
from databricks import sdk
from psycopg import sql
from psycopg_pool import ConnectionPool

# Database connection setup
workspace_client = sdk.WorkspaceClient()
postgres_password = None
last_password_refresh = 0
connection_pool = None

user_email = st.context.headers.get('X-Forwarded-Email')
user = workspace_client.current_user.me().user_name

def refresh_oauth_token():
    """Refresh OAuth token if expired."""
    global postgres_password, last_password_refresh
    if postgres_password is None or time.time() - last_password_refresh > 900:
        print("Refreshing PostgreSQL OAuth token")
        try:
            cred = workspace_client.database.generate_database_credential(
                request_id=str(uuid.uuid4()),
                instance_names=[os.getenv('LAKEBASE_INSTANCE_NAME')]
            )
            postgres_password = cred.token
            last_password_refresh = time.time()
        except Exception as e:
            st.error(f"❌ Failed to refresh token: {str(e)}")
            st.stop()

def get_connection_pool():
    """Get or create the connection pool."""
    global connection_pool
    if connection_pool is None:
        refresh_oauth_token()
        conn_string = (
            f"dbname={os.getenv('PGDATABASE')} "
            f"user={user} "
            f"password={postgres_password} "
            f"host={os.getenv('PGHOST')} "
            f"port={os.getenv('PGPORT')} "
            f"sslmode={os.getenv('PGSSLMODE', 'require')} "
            f"application_name={os.getenv('PGAPPNAME')}"
        )
        connection_pool = ConnectionPool(conn_string, min_size=2, max_size=10)
    return connection_pool

def get_connection():
    """Get a connection from the pool."""
    global connection_pool
    
    # Recreate pool if token expired
    if postgres_password is None or time.time() - last_password_refresh > 900:
        if connection_pool:
            connection_pool.close()
            connection_pool = None
    
    return get_connection_pool().connection()

def fetch_recommended_routes():
    """Fetch the recommended routes from Lakebase."""
    schema = os.getenv('LAKEBASE_SCHEMA')
    routes_table_name = os.getenv('LAKEBASE_ROUTES_TABLE_NAME')
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT part_id, priority, quantity_pending, due_date, recommended_machine_id, route_confidence
                FROM {schema}.{routes_table_name}
                ORDER BY priority DESC, due_date ASC
            """)
            return cur.fetchall()

def fetch_machines():
    """Fetch the machines from Lakebase."""
    schema = os.getenv('LAKEBASE_SCHEMA')
    routes_table_name = os.getenv('LAKEBASE_ROUTES_TABLE_NAME')
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT distinct recommended_machine_id
                FROM {schema}.{routes_table_name}
                ORDER BY 1 asc
            """)
            return cur.fetchall()

def fetch_parts():
    """Fetch the machines from Lakebase."""
    schema = os.getenv('LAKEBASE_SCHEMA')
    routes_table_name = os.getenv('LAKEBASE_ROUTES_TABLE_NAME')
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT distinct part_id,  
                    CAST(SUBSTRING(part_id FROM 'part_(.*)') AS INTEGER) as part_num
                FROM {schema}.{routes_table_name}
                ORDER BY part_num ASC
            """)
            return cur.fetchall()

def fetch_overrides():
    """Fetch current assignment overrides."""
    schema = os.getenv('LAKEBASE_SCHEMA')
    overrides_table = os.getenv('LAKEBASE_OVERRIDES_TABLE_NAME')
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT part_id, assigned_machine_id, assigned_by, assigned_at, notes
                FROM {schema}.{overrides_table}
                ORDER BY assigned_at DESC
            """)
            return cur.fetchall()

def add_override(part_id, assigned_machine_id, assigned_by, notes):
    """Add or update an assignment override."""
    schema = os.getenv('LAKEBASE_SCHEMA')
    overrides_table = os.getenv('LAKEBASE_OVERRIDES_TABLE_NAME')
    
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {schema}.{overrides_table} (part_id, assigned_machine_id, assigned_by, assigned_at, notes)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s)
            """, (part_id, assigned_machine_id, assigned_by, notes))
            conn.commit()

# Streamlit UI
def main():
    st.set_page_config(
        page_title="Shop Floor Routing Manager",
        page_icon="🏭",
        layout="wide"
    )
    
    st.title("🏭 Shop Floor Routing Manager")
    st.caption(f"Signed in as: {user_email}")

    # Load data
    try:
        recommended_routes_data = fetch_recommended_routes()
        machines_data = fetch_machines() 
        overrides_data = fetch_overrides()
        parts_data = fetch_parts()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

    st.subheader("Recommended Routes")
    try:
        if recommended_routes_data:
            import pandas as pd
            pd_recommended_routes = pd.DataFrame(recommended_routes_data, columns=['part_id', 'priority', 'quantity_pending', 'due_date', 'recommended_machine_id', 'route_confidence'])
            st.dataframe(pd_recommended_routes, use_container_width=True, hide_index=True)
            st.success(f"✅ Showing {len(recommended_routes_data)} recommended routes")
        else:
            st.info("No recommended routes found")
    except Exception as e:
        st.error(f"❌ Error loading routes: {str(e)}")
    
    # Assignment Overrides Section
    st.subheader("🔧 Assignment Overrides")
    # Add new override form
    st.write("**Add an Override:**")
    with st.form("override_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            part_id = st.selectbox("Select Part:", [row[0] for row in parts_data] if parts_data else [])
        
        with col2:
            assigned_machine_id = st.selectbox("Select Machine:", [row[0] for row in machines_data] if machines_data else [])
        
        with col3:
            notes = st.text_input("Reason:", placeholder="e.g., Maintenance required")
        
        submitted = st.form_submit_button("Set Override", type="primary")
        
        if submitted and part_id and assigned_machine_id and notes:
            try:
                add_override(part_id, assigned_machine_id, user_email or "Unknown", notes)
                st.success("✅ Override set successfully!")
                st.rerun()  # Refresh the page to show the new override
            except Exception as e:
                st.error(f"❌ Error setting override: {str(e)}")

    # Show past overrides
    try:        
        if overrides_data:
            st.write("**Override History:**")
            import pandas as pd
            pd_overrides = pd.DataFrame(overrides_data, columns=['part_id', 'assigned_machine_id', 'assigned_by', 'assigned_at', 'notes'])
            st.dataframe(pd_overrides, use_container_width=True, hide_index=True)
        else:
            st.info("No overrides currently set")
            
    except Exception as e:
        st.error(f"❌ Error loading overrides: {str(e)}")

if __name__ == "__main__":
    main() 
