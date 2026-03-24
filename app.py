def style_function(feature):
    return {
        'fillColor': 'green' if feature['properties']['mag'] > 5 else 'blue',
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.7
    }