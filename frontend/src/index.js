import '@riotjs/hot-reload'
import { component } from 'riot'
import App from './app.riot'
import registerGlobalComponents from './register-global-components'
import './components/assets/css/style.css'
import './components/assets/css/googlefonts.css'
import './components/assets/css/normalize.css'
import './components/assets/css/milligram.css'
import './components/assets/js/socket.io.min.js'
//import './riot-observable.js'
var riot = require('riot')
//var redux = require('redux')
//import { configureStore } from '@reduxjs/toolkit'
import observable from '@riotjs/observable'

/**
 * Trigger the old observable and the new event
 * @param   {RiotComponent} component - riot component
 * @param   {Function} callback - lifecycle callback
 * @param   {string} eventName - observable event name
 * @param   {...[*]} args - event arguments
 * @returns {RiotComponent|undefined}
 */
function triggerEvent(component, callback, eventName, ...args) {
    component.trigger(eventName, ...args)
    return callback.apply(component, [...args])
  }
  
  riot.install(function(componentAPI) {
    const {
        onBeforeMount,
        onMounted,
        onBeforeUpdate,
        onUpdated,
        onBeforeUnmount,
        onUnmounted
    } = componentAPI
  
    // make the riot component observable
    const component = observable(componentAPI)
    // remap the new event to the old ones
    const eventsMap = {
      onBeforeMount: ['before-mount', onBeforeMount],
      onMounted: ['mount', onMounted],
      onBeforeUpdate: ['before-update', onBeforeUpdate],
      onUpdated: ['updated', onUpdated],
      onBeforeUnmount: ['before-unmount', onBeforeUnmount],
      onUnmounted: ['unmount', onUnmounted]
    }
  
    Object.entries(eventsMap).forEach(([eventName, value]) => {
      const [oldObservableEvent, newCallback] = value
      component[eventName] = (...args) => triggerEvent(
        component, newCallback, oldObservableEvent, ...args
      )
    })
  
    return component
  })

// register
registerGlobalComponents()

// mount the root tag
component(App)(document.getElementById('root'))
