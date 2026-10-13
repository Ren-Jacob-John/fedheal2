# FedHeal Frontend Dashboard

Modern React 18 + Vite dashboard for clinicians, hospital administrators, and platform operators.

## Structure

```
frontend/
├── src/
│   ├── components/       # UI Components
│   │   ├── CasesView.jsx     # Patient cases, vitals entry, scan uploads & AI analysis review
│   │   ├── DetailDrawer.jsx  # Case detail inspection drawer
│   │   ├── FederationMap.jsx # Interactive 3D/canvas federation topology
│   │   ├── FlaggedReview.jsx # Review flagged vitals and outlier alerts
│   │   ├── LoginGate.jsx     # Authentication dialog & session keeper
│   │   ├── RoundsRail.jsx    # Retraining rounds & candidate inspection
│   │   ├── ShapChart.jsx     # Visual feature importance attribution
│   │   ├── SynthesisView.jsx # Multi-modal synthesis & clinical review packet
│   │   ├── SystemMap.jsx     # Microservice topology view
│   │   ├── TopHUD.jsx        # Navigation bar, user role badge, hospital context
│   │   └── UploadPanel.jsx   # Clinical vitals & imaging upload interface
│   ├── styles/           # CSS design system
│   │   ├── app.css           # Core application layouts
│   │   ├── global.css        # Typography, animations & reset
│   │   └── tokens.css        # Color palette, spacing, elevations
│   ├── api.js            # API client for backend services (:8001, :8005, :8006)
│   ├── App.jsx           # Main application view container
│   └── main.jsx          # React DOM entry point
├── public/               # Static assets & favicons
├── package.json          # Dependencies & scripts
└── vite.config.js        # Vite dev server configuration
```

## Running Locally

```bash
# 1. Install dependencies
npm install

# 2. Run development server (http://localhost:5173)
npm run dev

# 3. Build production bundle
npm run build
```

## Environment Variables

Configured via `.env` or defaults:
- `VITE_AUTH_API_BASE`: Auth Service URL (default: `http://localhost:8001`)
- `VITE_ADMIN_API_BASE`: Admin / Model Registry URL (default: `http://localhost:8005`)
- `VITE_SYNTHESIS_API_BASE`: Synthesis / Analysis API URL (default: `http://localhost:8006`)
