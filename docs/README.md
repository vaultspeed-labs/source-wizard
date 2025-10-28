# VaultSpeed Source Wizard

A Streamlit application for creating sources in VaultSpeed using the vaultspeed_sdk.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- VaultSpeed account and API access
- vaultspeed-sdk package

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd source_wizard
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

Or using Streamlit directly:
```bash
streamlit run src/vaultspeed_wizard/main.py
```

## 📁 Project Structure

```
source_wizard/
├── src/
│   └── vaultspeed_wizard/     # Main application package
│       ├── __init__.py
│       ├── main.py            # Main application logic
│       ├── utils.py           # Utility functions
│       ├── sessionState.py    # Session state management
│       ├── prerequisites.py   # Prerequisites checking
│       ├── systemParam.py     # System parameters
│       ├── create.py          # Source/project creation
│       ├── impParam.py        # Important parameters
│       ├── CDCParam.py        # CDC parameters
│       ├── contact_sales.py   # Contact sales
│       └── dataProfiling.py   # Data profiling (placeholder)
├── config/
│   └── settings.py            # Configuration settings
├── docs/
│   └── README.md              # This documentation
├── app.py                     # Application entry point
├── requirements.txt           # Python dependencies
└── README.md                  # Main project README
```

## 🔧 Configuration

Edit `config/settings.py` to modify:
- VaultSpeed API URL
- Application settings
- Default timeouts and retry values

## 🛠️ Development

### Adding New Steps
1. Create a new function in the appropriate module
2. Add the step to the main routing logic in `main.py`
3. Update the step flow as needed

### Session State Management
Use `sessionState.py` for persistent session management across application restarts.

## 📚 API Reference

The application uses the VaultSpeed SDK for all API interactions. Key components:
- `Client`: Main API client
- `System`: System-level operations
- `Project`: Project management
- `Source`: Source configuration

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

[Add your license information here]
