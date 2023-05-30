export default [{
  path: '/',
  label: 'ZusammenPlayer',
  componentName: 'home'
}, {
  path: '/about',
  label: 'About',
  componentName: 'about'
}, {
  path: '/project',
  label: 'Project',
  componentName: 'project'
},
{
  path: '/project/:slug',
  label: 'Project',
  componentName: 'project-details'
}]