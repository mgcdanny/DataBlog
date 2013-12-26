
var app = angular.module('angApp', ['ngGrid', 'ngResource', 'ngRoute']);

app.config(['$routeProvider', '$locationProvider', function($routeProvider,$locationProvider){
	//$locationProvider.html5Mode(true);
	$routeProvider.
      when('/', {
        templateUrl: 'static/html/home.html',
        controller: ''
      }).when('/table/:name', {
        templateUrl: 'static/html/table.html',
        controller: 'angCtrl'
      }).otherwise({
        redirectTo: '/'
      });
	}]);


app.factory('RestService', ['$resource', function($resource) {
    return $resource('/api/:name', {name: 'test'});
}]);


app.controller('getAllDataCtrl', ['$scope', '$http', function($scope,$http){
    $http.get('/api/allTables').success(function(response){
        $scope.allTables = response;
    });
}]);


app.controller('angCtrl', ['$scope', '$location', '$routeParams', 'RestService', function($scope, $location, $routeParams, RestService) {

    RestService.get($routeParams, function(response){
        console.log(angular.fromJson(response.theData));
    	$scope.myData = angular.fromJson(response.theData);
    });

    $scope.filterOptions = {filterText: ''};
	$scope.mySelections = [];
    $scope.gridOptions = {
    	data: 'myData', 
    	enableColumnResize: true, 
    	showGroupPanel: true,  
    	jqueryUIDraggable: true,
        multiSelect: false, 
        showFooter:true,
   	 	filterOptions: $scope.filterOptions,
    	selectedItems: angular.fromJson($scope.mySelections),
        showColumnMenu: true
    }

}]);

