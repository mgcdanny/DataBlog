
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
      }).when('/upload', {
        templateUrl: 'static/html/upload.html',
        controller: ''
      }).otherwise({
        redirectTo: '/'
      });
	}]);

app.factory('RESTService', ['$resource', function($resource) {
    return $resource('/api/:name', {name: 'RESTServiceTest'}, {updateRow: {method:'PUT'}});
}]);

app.controller('getAllDataCtrl', ['$scope', '$http', 'RESTService', function($scope,$http, RESTService){
    
    var getAllTables = function(){
            $http.get('/api/allTables').success(
                function(response){
                    $scope.allTables = response;
                }
            )}
    /*calling this function here seems hackish but did not see better way*/
    getAllTables();

    $scope.deleteCsvFile = function(thePageUri){
        RESTService.delete({name: thePageUri}, function(response){
            getAllTables();
        });
    }

    $scope.setFile = function (element) {
        $scope.uploadedFile = element.files[0];
        
    }

    $scope.uploadFile = function () {
        if (!$scope.uploadedFile) {
            return;
        }
        var fd = new FormData();
        fd.append("upFile", $scope.uploadedFile);
        console.log(fd)
        $http.post('/api/upload', fd, {
                headers:{
                    'Content-Type': undefined 
                },
                transformRequest: angular.identity
            }).success(function(){
                getAllTables()
            });
    };
 }]);

app.controller('angCtrl', ['$scope', '$location', '$routeParams', 'RESTService', function($scope, $location, $routeParams, RESTService) {
    RESTService.get($routeParams, function(response){
    	$scope.myData = angular.fromJson(response.theData);
        /*to hide the row, name, columns for being displayed*/
        $scope.myColumnDefs = [];
        angular.forEach($scope.myData[0], function(v,k){
            if(k == 'row' || k == 'name'){
                $scope.myColumnDefs.push({field: k, visible:false})
            } else {
                $scope.myColumnDefs.push({field: k, visible:true})
            }
        });
    });

  
    $scope.updateRow = function(data){
        RESTService.updateRow($routeParams, data)
    }

    $scope.hidePrimaryKey = function(data){
        if(data == 'row' || data == 'name'){
            return false
        }else{
            return true
        }
    }


    $scope.filterOptions = {filterText: ''};
    $scope.mySelections = [];
    $scope.gridOptions = {
    	data: 'myData', 
    	enableColumnResize: true,
        keepLastSelected: false, 
    	showGroupPanel: false,  
    	jqueryUIDraggable: false,
        multiSelect: false, 
        showFooter:true,
   	 	filterOptions: $scope.filterOptions,
    	selectedItems: $scope.mySelections,
        showColumnMenu: true,
        columnDefs: 'myColumnDefs'
    }
}]);


