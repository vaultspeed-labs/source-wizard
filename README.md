# VaultSpeed Source Wizard

A Streamlit application for creating sources in VaultSpeed using the vaultspeed_sdk. This wizard guides you through the complete process of setting up a new source, from authentication to configuration. It gives guidance in the process of setting up the source parameters for a new source. 

This tool is aimed to support customers to more thouroughly understand the most forgotten/important parameters hidden in the long list of parameters supported by VaultSpeed

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **VaultSpeed account**
- **vaultspeed-sdk** package

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/VaultSpeedPSE/source-wizard.git
   cd source-wizard
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   ```
   
   Move the [`pip.conf`](pip.conf) file found in this repo into the newly created `venv` folder and fill in the `<username>` and `<password>` fields.

3. **Activate the virtual environment:**
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

   The application will open in your default web browser at `http://localhost:8501`

## 📋 What This Wizard Does

The VaultSpeed Source Wizard guides you through the following steps:

1. **Login** - Authenticate with your VaultSpeed credentials
2. **Prerequisites** - Check system prerequisites
3. **Source Creation** - Create a new source
4. **System Parameters** - Configure system-level settings
5. **Important Parameters** - Configure key source parameters
6. **CDC Configuration** - Set up Change Data Capture settings
7. **Completion** - Source is ready to use in VaultSpeed

## Application Flow

On the login screen, you'll need to provide:

- **VaultSpeed API URL** - Default is `https://app.vaultspeed.com/api` (can be changed for different environments, **don't forget the /api**)
- **Username** - Your VaultSpeed username
- **Password** - Your VaultSpeed password

After authenticating you get guided through the creation of a complete source, focussing on the most important parameters or the parameters that are forgotten/wrongfully set by users.

## 📁 Project Structure

```
source_wizard/
├── src/
│   └── vaultspeed_wizard/          # Main application package
│       ├── __init__.py
│       ├── main.py                 # Main application logic and routing
│       ├── utils.py                 # Utility functions for UI components
│       ├── sessionState.py          # Session state management
│       ├── prerequisites.py        # Prerequisites checking
│       ├── systemParam.py           # System parameters configuration
│       ├── create.py                # Source and project creation
│       ├── impParam.py              # Important parameters configuration
│       ├── CDCParam.py              # CDC parameters configuration
│       ├── contact_sales.py         # Contact sales page
│       └── dataProfiling.py         # Data profiling functionality
├── app.py                           # Application entry point
├── requirements.txt                 # Python dependencies
└── README.md                        # This file
```

## 📦 Dependencies

The project has minimal dependencies:

- **streamlit** - Web application framework
- **vaultspeed-sdk** - VaultSpeed Python SDK installed through the [`pip.conf`](pip.conf)
