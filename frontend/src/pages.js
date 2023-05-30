export default [{
  path: '/',
  label: 'ZusammenPlayer',
  componentName: 'home'
}, {
  path: '/project',
  label: 'Project',
  componentName: 'project'
}, {
  path: '/debug',
  label: 'Debugging',
  componentName: 'debug-page'
},
{
  path: '/project/:slug',
  label: 'Project',
  componentName: 'project-details'
}]