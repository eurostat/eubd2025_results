def get_nav_bar_html():
    return """
    <nav class="navbar">
      <div class="nav-container">
        <a href="/" class="nav-link">Surface & Air Temperature</a>
        <a href="/soil_moisture" class="nav-link">Soil Moisture</a>
        <a href="/tasmi" class="nav-link">Thermal Anomaly Index</a>

        <a href="/drought_index" class="nav-link">Drought Index</a>
        <a href="/agriculture" class="nav-link">Space Planter</a>
        <a href="/spacial_analysis" class="nav-link">Spacial Analysis</a>
        <a href="/forecasts" class="nav-link">Forecasts</a>
        <a href="/docs" class="nav-link">Docs</a>
      </div>
      <div style="text-align:center; margin-bottom:60px;">
        <img src="/static/qr.png" alt="QR Code" style="max-width:100px;">
      </div>
    </nav>
    """