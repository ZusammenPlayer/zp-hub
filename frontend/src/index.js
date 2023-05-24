import '@riotjs/hot-reload'
import { component } from 'riot'
import App from './app.riot'
import registerGlobalComponents from './register-global-components'
import './components/assets/css/style.css'
import './components/assets/css/googlefonts.css'
import './components/assets/css/normalize.css'
import './components/assets/css/milligram.css'
import './components/assets/js/socket.io.min.js'


// register
registerGlobalComponents()

// mount the root tag
component(App)(document.getElementById('root'))
