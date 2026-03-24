def style_function(feature):
    color = 'blue' if feature['properties']['type'] == 'A' else 'green'
    return {'color': color}
