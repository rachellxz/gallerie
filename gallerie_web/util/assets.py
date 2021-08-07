from flask_assets import Bundle

bundles = {
    'home_js':
    Bundle('js/custom.js', filters='jsmin', output='gen/home.%(version)s.js'),
    'home_css':
    Bundle('css/custom.css',
           filters='cssmin',
           output='gen/home.%(version)s.css'),
}
