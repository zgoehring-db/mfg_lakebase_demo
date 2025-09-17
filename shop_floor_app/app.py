import streamlit as st
from databricks import sdk
from data_access import (
    fetch_recommended_routes,
    fetch_machines,
    fetch_parts,
    fetch_overrides,
    add_override,
    part_lookup,
    count_overdue_parts
)
from table_styling import get_table_styles, create_scrollable_table

# Get user information
workspace_client = sdk.WorkspaceClient()
user_email = st.context.headers.get('X-Forwarded-Email')
user = workspace_client.current_user.me().user_name

# Streamlit UI
def main():
    st.set_page_config(
        page_title="Shop Floor Routing Manager",
        page_icon="🏭",
        layout="wide"
    )
    
    
    # Load external CSS file
    import os
    
    def load_css():
        css_path = os.path.join(os.path.dirname(__file__), 'styles.css')
        with open(css_path, 'r') as f:
            return f.read()
    
    st.markdown(f"<style>{load_css()}</style>", unsafe_allow_html=True)
    
    # Modern dashboard header
    st.markdown("""
    <div class="dashboard-header">
        <h1>Shop Floor Routing Manager</h1>
        <div class="user-info">👤 {}</div>
    </div>
    """.format(user_email), unsafe_allow_html=True)

    # Load data
    try:
        recommended_routes_data = fetch_recommended_routes()
        machines_data = fetch_machines() 
        overrides_data = fetch_overrides()
        parts_data = fetch_parts()
        overdue_count = count_overdue_parts()
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        st.stop()

    # Shop Floor Metrics - Modern Cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card" style="min-height: 200px; display: flex; flex-direction: column; justify-content: center;">
            <h2 class="metric-header">Overdue Parts</h2>
            <div class="metric-value" style="color: #ff4444;">{}</div>
            <div class="metric-description" style="color: {};">{}</div>
        </div>
        """.format(
            overdue_count,
            "#ff6666" if overdue_count > 0 else "#44aa44",
            "⚠️ Attention Required" if overdue_count > 0 else "✅ All On Track"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card" style="min-height: 200px; display: flex; flex-direction: column; justify-content: center;">
            <h2 class="metric-header">Total Parts</h2>
            <div class="metric-value" style="color: #4444ff;">{}</div>
            <div class="metric-description" style="color: #6666ff;">In Production Queue</div>
        </div>
        """.format(len(recommended_routes_data)), unsafe_allow_html=True)
    
    with col3:
        high_priority = len([r for r in recommended_routes_data if r[1] == "high"])
        st.markdown("""
        <div class="metric-card" style="min-height: 200px; display: flex; flex-direction: column; justify-content: center;">
            <h2 class="metric-header">High Priority Parts</h2>
            <div class="metric-value" style="color: #ff8800;">{}</div>
            <div class="metric-description" style="color: #ffaa00;">Urgent Processing</div>
        </div>
        """.format(high_priority), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card" style="min-height: 200px; display: flex; flex-direction: column; justify-content: center;">
            <h2 class="metric-header">Manual Overrides</h2>
            <div class="metric-value" style="color: #8844ff;">{}</div>
            <div class="metric-description" style="color: #aa66ff;">Overrides Made</div>
        </div>
        """.format(len(overrides_data)), unsafe_allow_html=True)
    
    # Main content in card
    st.markdown("""
    <div style="background: white; padding: 8px 20px; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: 1px solid rgba(0,0,0,0.05); margin-bottom: 1rem;">
        <h2 style="margin: 0; color: #2c3e50; font-size: 2em; line-height: 1.2; font-weight: 600;">Shop Floor Operations</h2>
    </div>
    """, unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs([
        "📋 **Recommended Routes**", 
        "🔍 **Part Lookup**", 
        "🔧 **Manual Overrides**"
    ])
    
    with tab1:
        # st.subheader("📋 Recommended Part to Machine Routes")
        try:
            if recommended_routes_data:
                import pandas as pd
                pd_recommended_routes = pd.DataFrame(recommended_routes_data, columns=['part_id', 'priority', 'quantity_pending', 'due_date', 'recommended_machine_id', 'route_confidence'])
                summary_df = pd_recommended_routes[['part_id', 'priority', 'due_date', 'recommended_machine_id', 'route_confidence']]
                
                st.markdown('<p class="instruction-text">For more detailed part information, use the Part Lookup tab</p>', unsafe_allow_html=True)
                
                # Add simple sorting controls
                col1, col2 = st.columns([1, 1])
                with col1:
                    sort_by = st.selectbox("Sort by:", ["Part ID", "Priority", "Due Date", "Recommended Machine", "Route Confidence"])
                with col2:
                    sort_order = st.selectbox("Order:", ["Ascending", "Descending"])
                
                # Apply sorting
                if sort_by == "Part ID":
                    summary_df = summary_df.sort_values('part_id', ascending=(sort_order == "Ascending"))
                elif sort_by == "Priority":
                    summary_df = summary_df.sort_values('priority', ascending=(sort_order == "Ascending"))
                elif sort_by == "Due Date":
                    summary_df = summary_df.sort_values('due_date', ascending=(sort_order == "Ascending"))
                elif sort_by == "Recommended Machine":
                    summary_df = summary_df.sort_values('recommended_machine_id', ascending=(sort_order == "Ascending"))
                elif sort_by == "Route Confidence":
                    summary_df = summary_df.sort_values('route_confidence', ascending=(sort_order == "Ascending"))
                
                # Apply table styling and create scrollable container
                styled_df = summary_df.style.set_table_styles(get_table_styles())
                scrollable_table = create_scrollable_table(styled_df)
                st.markdown(scrollable_table, unsafe_allow_html=True)
            else:
                st.info("No recommended routes found")
        except Exception as e:
            st.error(f"❌ Error loading routes: {str(e)}")
    
    with tab2:
        # st.subheader("🔍 Part Lookup")
        
        col1, col2 = st.columns([1.5, 2])
        
        with col1:
            st.markdown('<p class="instruction-text">Select a part to lookup and then click "Lookup Part"</p>', unsafe_allow_html=True)

            selected_part = st.selectbox(" ", 
                                        [row[0] for row in parts_data] if parts_data else [],
                                        key="part_lookup")
            
            if st.button("Lookup Part", key="lookup_btn", type="primary"):
                part_data = part_lookup(selected_part)
                
                if part_data:
                    # Unpack all the fields from the part backlog table (14 fields + query_time)
                    (part_id, priority, quantity, due_date, material, part_type, 
                     quality_level, surface_finish, tolerance, weight_kg, 
                     dimensions, drawing_number, revision, estimated_hours, query_time) = part_data
                    
                    st.success(f"✅ Found in {query_time}ms")
                    st.caption("*Timing includes network latency, authentication, database connection setup, SQL query execution, etc.")
                    
                    with col2:
                        st.markdown('<p class="instruction-text">Part Details:</p>', unsafe_allow_html=True)
                        
                        # Organize the data into logical sections
                        col2a, col2b = st.columns(2)
                        
                        with col2a:
                            st.markdown('<h5 style="color: #2c3e50; margin-bottom: 10px;">📋 Basic Information</h3>', unsafe_allow_html=True)
                            st.json({
                                "Part ID": part_id,
                                "Priority": priority,
                                "Quantity Pending": quantity,
                                "Due Date": str(due_date),
                                "Material": material,
                                "Part Type": part_type
                            })
                            
                            st.markdown('<h5 style="color: #2c3e50; margin-bottom: 10px;">⚙️ Technical Specifications</h3>', unsafe_allow_html=True)
                            st.json({
                                "Quality Level": quality_level,
                                "Surface Finish": surface_finish,
                                "Tolerance": tolerance,
                                "Weight (kg)": weight_kg,
                                "Dimensions": dimensions
                            })
                        
                        with col2b:
                            st.markdown('<h5 style="color: #2c3e50; margin-bottom: 10px;">📐 Engineering Details</h3>', unsafe_allow_html=True)
                            st.json({
                                "Drawing Number": drawing_number,
                                "Revision": revision,
                                "Estimated Hours": estimated_hours
                            })
                else:
                    st.error("❌ Part not found")
        
        with col2:
            pass
    
    with tab3:
        # st.subheader("🔧 Route Assignment Manual Overrides")
        st.markdown('<p class="instruction-text">Submit a part-to-machine override if the recommended route needs to be changed due to machine downtime, maintenance, or other operational constraints</p>', unsafe_allow_html=True)
        
        # Add new override form
        st.markdown('<p class="manual-overrides-section-header">Add an Override:</p>', unsafe_allow_html=True)
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
                st.markdown('<p class="manual-overrides-section-header">Override History:</p>', unsafe_allow_html=True)
                import pandas as pd
                pd_overrides = pd.DataFrame(overrides_data, columns=['part_id', 'assigned_machine_id', 'assigned_by', 'assigned_at', 'notes'])
                
                # Use simple st.dataframe for override history
                st.dataframe(pd_overrides, use_container_width=True)
            else:
                st.info("No overrides currently set")
                
        except Exception as e:
            st.error(f"❌ Error loading overrides: {str(e)}")

if __name__ == "__main__":
    main() 
