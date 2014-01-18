//consider using SlickGrid (github: slickgrid) instead of ngGrid

var app = angular.module('angApp', ['ngGrid', 'ngResource', 'ngRoute']);

app.filter('html', function($sce) {
    //allows html to be renderd after interpoltion
    //$sce must be injected into the controller
    return function(val) {
        return $sce.trustAsHtml(val)
    };
});

app.config(['$routeProvider', '$locationProvider', function($routeProvider,$locationProvider){
	//$locationProvider.html5Mode(true);
	$routeProvider.
      when('/', {
        templateUrl: 'static/html/home.html',
        controller: ''
      }).when('/table/:name', {
        templateUrl: 'static/html/table.html'
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

/*Two post calls: first for the meta data, second for the actual file*/
/*I can't figure out how to send the file and the data abou the file at the same time*/         

    $scope.upFileTitle = ""
    $scope.upFileDesc = ""

    $scope.setFile = function (element) {        
        $scope.upFile = element.files[0];
    }

    $scope.uploadAll = function(){
        formData = new FormData()
        formData.append("upFileTitle",$scope.upFileTitle)
        formData.append("upFileDesc",$scope.upFileDesc)
        formData.append("upFile",$scope.upFile)
        $http.post("/api/upload", formData, {
            headers: { 'Content-Type': undefined },
            transformRequest: angular.identity
        }).success(function(){
            getAllTables()
        });
    }
 }]);

app.controller('angCtrl', ['$scope', '$location', '$routeParams', 'RESTService', '$http', '$sce', function($scope, $location, $routeParams, RESTService, $http, $sce) {
    
    RESTService.get($routeParams, function(response){
    	$scope.myData = angular.fromJson(response.theData);
        /*to hide the row, name, columns for being displayed*/
        $scope.myColumnDefs = [];
        angular.forEach($scope.myData[0], function(v,k){
            if(k == 'row' || k == 'name'){
                $scope.myColumnDefs.push({field: k, visible:false, enableCellEdit: false})
            } else {
                $scope.myColumnDefs.push({
                    field: k, visible:true,  
                    enableCellEdit: true, 
                    cellTemplate: cssCellTemplate, 
                    editableCellTemplate: cssCellEditTemplate
                })
            }
        });
    });

    // Update Entity on the server side
    $scope.updateEntity = function (column, row) {
        $scope.updateRow(row.entity)
        //console.log(row.entity);
        //console.log(column.field);
    }    

    $scope.getMeta = function(){
        $http.get('/api/meta/'+$routeParams['name'])
            .success(
                function(response){
                    $scope.csvMeta = response
                    //angular.forEach($scope.csvMeta, function(v,k){
                      //  $scope.csvMeta[k] = v.replace(/\n/g, '<br/>')
                    //})
                })
        }
    $scope.getMeta()

    $scope.putMeta = function(){
        $http.put('/api/meta/'+$routeParams['name'], $scope.csvMeta)
            .success(function(){console.log($scope.csvMeta)})
        }
    
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

    var cssCellEditTemplate = "<input ng-class=\"'colt' + col.index\" ng-input=\"COL_FIELD\" ng-model=\"COL_FIELD\" ng-blur=\"updateEntity(col, row)\"/>"
    var cssCellTemplate = "<div title=\"{{row.getProperty(col.field)}}\"><div class=\"ngCellText\">{{row.getProperty(col.field)}}</div></div>"
    $scope.filterOptions = {filterText: ''};
    $scope.mySelections = [];
    $scope.gridOptions = {
    	data: 'myData', 
    	enableColumnResize: true,
        enableCellEdit: true,
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


