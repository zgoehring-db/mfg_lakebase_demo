# Manufacturing Lakebase Demo

A demonstration of Databricks Lakebase capabilities for shop floor routing management. This app shows how to use Lakebase (PostgreSQL-compatible) for real-time manufacturing data with AI-powered routing recommendations.

## 🏭 What This Demo Shows

- **Sync data from Unity Catalog to Lakebase with Synced Tables** 
- **Write data directly to Lakebase** 
- **Integrate Lakebase with Databricks Apps**

## 🚀 Quick Start

### Prerequisites

- Databricks workspace with Lakebase access
- Databricks Apps enabled in your workspace

### 1. Setup Data Pipeline

1. **Upload the notebooks** to your Databricks workspace
2. **Run `dummy_data_gen/data_gen.ipynb`** to create sample manufacturing data
3. **Run `lakebase_setup/lakebase_setup.ipynb`** to:
   - Set up DLT pipeline for data sync
   - Start the pipeline to sync data to Lakebase

### 2. Deploy the App

1. **Create a new Databricks App** in your workspace
2. **Upload the `shop_floor_app/` folder** to your app
3. **Set environment variables** in the app settings:
   - `LAKEBASE_INSTANCE_NAME`: Your Lakebase instance name
   - `LAKEBASE_SCHEMA`: Schema name (e.g., `mfg_lakebase_demo`)
   - `LAKEBASE_ROUTES_TABLE_NAME`: `recommended_routes_synced_table`
   - `LAKEBASE_OVERRIDES_TABLE_NAME`: `assignment_overrides`
4. **Deploy and run** the app!

The app will automatically use your workspace authentication and connect to Lakebase.

### 3. Local Development (Optional)

If you want to run locally for development:

```bash
git clone <your-repo-url>
cd mfg_lakebase_demo

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r shop_floor_app/requirements.txt

# Configure environment
cp .envrc.example .envrc
# Edit .envrc with your values

# Run locally
streamlit run shop_floor_app/app.py
```

## 📁 Project Structure

```
mfg_lakebase_demo/
├── shop_floor_app/           # Streamlit web application
│   ├── app.py               # Main application code
│   ├── app.yaml             # Databricks App configuration
│   └── requirements.txt     # Python dependencies
├── lakebase_setup/          # Data pipeline setup
│   └── lakebase_setup.ipynb # DLT pipeline and data creation
├── dummy_data_gen/          # Sample data generation
│   └── data_gen.ipynb      # Manufacturing data creation
├── .envrc.example          # Environment variables template
└── README.md               # This file
```

## 🔧 Features

### Shop Floor Routing Manager

- **View Recommended Routes**: See AI-powered part-to-machine assignments
- **Assignment Overrides**: Log manual routing decisions
- **Real-time Data**: Live sync from Delta tables to Lakebase
- **User Tracking**: See who made what decisions and when

### Data Tables

- `recommended_routes_synced_table`: AI recommendations with confidence scores
- `part_backlog_synced_table`: Manufacturing backlog with priorities
- `assignment_overrides`: Manual override log

## 📊 Data Schema

### Recommended Routes
- `part_id`: Part identifier
- `priority`: Manufacturing priority
- `quantity_pending`: Units to be produced
- `due_date`: Production deadline
- `recommended_machine_id`: AI-suggested machine
- `route_confidence`: Confidence score

### Assignment Overrides
- `part_id`: Part identifier
- `assigned_machine_id`: Manually chosen machine
- `assigned_by`: User who made the decision
- `assigned_at`: Timestamp of decision
- `notes`: Additional context

