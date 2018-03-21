var myApp = angular.module('myApp', ['admin','ngRoute','angularMoment','ui.bootstrap']);

myApp.config(function ($routeProvider) {
  $routeProvider
    .when('/', {
      templateUrl: 'static/partials/home.html',
      access: {restricted: true}
    })
    .when('/login', {
      templateUrl: 'static/partials/login.html',
      controller: 'loginController',
      access: {restricted: false}
    })
    .when('/logout', {
      controller: 'logoutController',
      access: {restricted: true}
    })
      .when('/profile/:id', {
      controller: 'profileController',
      templateUrl: 'static/partials/user/profile.html',
      access: {restricted: true}
    })
       .when('/account/:user', {
      controller: 'accountController',
      templateUrl: 'static/partials/user/account.html',
      access: {restricted: true}
    })
    .otherwise({
      redirectTo: '/account/:user'
    });
})
;

myApp.run(function ($rootScope, $location, $route, AuthService) {
  $rootScope.$on('$routeChangeStart',
    function (event, next, current) {
      AuthService.getUserStatus()
      .then(function(){
        if (next.access.restricted && !AuthService.isLoggedIn()){
          $location.path('/login');
          $route.reload();
        }
      });
  });
});