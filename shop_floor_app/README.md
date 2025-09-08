# Manufacturing Lakebase Demo

A Streamlit application for shop floor routing management with Databricks integration.

## Local Development Setup

### 1. Create and Activate Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Application

For local development with mock data:
```bash
streamlit run databricks_app/app_local.py
```

For production with Databricks integration:
```bash
streamlit run databricks_app/app.py
```

### 3. Deactivate Virtual Environment

When you're done:
```bash
deactivate
```

## Files

- `databricks_app/app.py` - Production app with Databricks integration
- `databricks_app/app_local.py` - Local development app with mock data
- `requirements.txt` - Python dependencies

## Dependencies

- streamlit
- pandas
- databricks-sql-connector
- pyspark
- python-dotenv
