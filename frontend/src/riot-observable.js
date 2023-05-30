// riot-observable-plugin.js

import observable from 'riot-observable'

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
