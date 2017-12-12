(function () {

  'use strict';

 angular.module('apiApp', [])
  .config(['$interpolateProvider', function($interpolateProvider) {
	  $interpolateProvider.startSymbol('{-');
	  $interpolateProvider.endSymbol('-}');
	}])

  .controller('MainController', ['$scope', '$log', '$http',
	  function($scope, $log, $http) {

	  	$scope.users = [];
	  $scope.getUsers = function() {


	    $http.get('/prt/api/v1.0/users',  {headers: {
	    'Authorization': 'Basic cm9vdDp0b29y'}}).
		      success(function(results) {
		      	$scope.users = results;
		        console.log($scope.users);
		      }).
		      error(function(error) {
		        console.log(error)
		      });

		  };

	  $scope.getUsers();

	}
	]);


}());