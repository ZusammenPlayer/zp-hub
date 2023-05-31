export default [{
  path: '/',
  label: 'ZusammenPlayer',
  componentName: 'home'
}, {
  path: '/about',
  label: 'About',
  componentName: 'about'
}, {
  path: '/debug',
  label: 'Debugging',
  componentName: 'debug'
},
{
  path: '/project/:slug',
  label: 'Project',
  componentName: 'projectdetail'
},
{
  path: '/project/:slug/:action',
  label: 'Project',
  componentName: 'projectdetail'
}]