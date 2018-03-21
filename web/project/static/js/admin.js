var myApp = angular.module('admin', ['ngRoute','angularMoment','ui.bootstrap']);

myApp.config(function ($routeProvider) {
  $routeProvider
      .when('/admin/register', {
      templateUrl: 'static/partials/register.html',
      controller: 'registerController',
      access: {restricted: true, admin:true}
    })
      .when('/admin/password', {
      templateUrl: 'static/partials/admin/password.html',
      controller: 'adminpasswordController',
      access: {restricted: true, admin:true}
    })
     .when('/admin/listuser', {
      templateUrl: 'static/partials/admin/listuser.html',
      controller: 'adminlistuserController',
      access: {restricted: true, admin:true}
    })

});
