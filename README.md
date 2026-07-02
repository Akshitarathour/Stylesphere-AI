# StyleSphere AI 👗✨

StyleSphere AI is an advanced, production-grade, cognitive wardrobe organizer and styling recommendation application. It uses the official `groq` SDK and a coordinated multi-agent architecture to classify garments, check weather and occasion compliance, track clothing usage and sustainability scores, and generate travel checklists and shopping advice.

## Features & Pages
1. **🏠 Home**: Dashboard with daily styling formulas, dynamic weather widget, and total wardrobe utilization.
2. **👚 Wardrobe**: Category filter gallery showing all saved clothes, details, and wear counts.
3. **📤 Upload Clothing**: Vision pipeline auto-detecting colors, sleeve length, season suitability, and fabric from photos.
4. **💡 Outfit Recommendation**: Intelligent matching agent recommending 1-2 styling combos using color theory and weather constraints.
5. **📅 Today's Outfit**: Log today's worn garments to automatically compile wear history and calculate utility.
6. **📊 Wardrobe Analytics**: Interactive category distributions and Cost-Per-Wear (CPW) insights.
7. **🌿 Sustainability**: utilization index, fabric assessment, and AI-generated green fashion reports.
8. **✈️ Travel Packing**: Minimalist capsule travel checklist generator.
9. **🛍️ Shopping Advisor**: Multi-dimensional pre-purchase auditor validating duplication risks and versatility ratings.
10. **⚙️ Settings**: Groq API configuration and profile style vibe tuning.

## Multi-Agent Architecture
- **Closet Agent**: Manages the SQLite database and wardrobe inventory CRUD operations.
- **Image Recognition Agent**: Analyzes garment photos to extract structured metadata (JSON mode).
- **Style Recommendation Agent**: Coordinates outfit creation using color harmony principles.
- **Weather Agent**: Injects real-time weather styling rules, layer suggestions, and caution alerts.
- **Occasion Agent**: Defines dress codes and style profiles (Interview, Wedding, College, etc.).
- **Sustainability Agent**: Computes utilization rates and writes green advisory reports.
- **Packing Agent**: Formulates minimalist capsule checklists based on length and destination.
- **Shopping Advisor Agent**: Audits purchase value, versatility score, and flags duplicate buys.
- **Fashion Trend Agent**: Suggests classic trend rules (Sandwich rule, Third Piece rule).
- **Personal Preference Agent**: Customizes styling suggestions to color preferences and learned vibes.

## Getting Started

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Initialize and run:
   ```bash
   python main.py
   ```
   Or run the Streamlit app directly:
   ```bash
   streamlit run app.py
   ```

### API Configuration
To unlock the full potential of StyleSphere's AI agents, enter your Groq API Key in the **Settings** sidebar tab or configure it via a `.env` file or environment variable:
```bash
set GROQ_API_KEY=your_groq_api_key
```
## AI Models Used

- **Google Gemini** – Used for garment image recognition and metadata extraction (category, color, fabric, pattern, sleeve type, etc.).
- **Groq LLM** – Powers the multi-agent system, including outfit recommendations, weather styling, shopping advisor, sustainability reports, travel packing, fashion trends, and personalized styling assistance.