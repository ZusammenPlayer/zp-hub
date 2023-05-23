import './style.css'
import '@riotjs/hot-reload'
import { mount } from 'riot'
import registerGlobalComponents from './register-global-components'
import { Route, Router } from '@riotjs/route'
import { register } from 'riot'

// register
registerGlobalComponents()
register('router', Router)
register('route', Route)

// mount all the global components found in this page
mount('[data-riot-component]')
