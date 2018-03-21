var myApp = angular.module('myApp');

myApp
    .controller('mainController', ['$scope', '$location', 'AuthService',
        function($scope, $location, AuthService) {
            // call login from service
            AuthService.getUserStatus()
                .then(function() {
                    $scope.isLoggedIn = AuthService.isLoggedIn();
                    if ($scope.isLoggedIn) {
                        $scope.user = AuthService.getUser();
                    }
                })
        }
    ])
    .controller('loginController', ['$scope', '$location', 'AuthService',
        function($scope, $location, AuthService) {

            $scope.login = function() {

                // initial values
                $scope.error = false;
                $scope.disabled = true;

                // call login from service
                AuthService.login($scope.loginForm.name, $scope.loginForm.password)
                    // handle success
                    .then(function(user) {
                        $scope.disabled = false;
                        $scope.loginForm = {};
                        if (user.admin) {
                            $location.path('/admin/listuser');
                        } else {
                            $location.path('/account/' + user.name);
                        }
                    })
                    // handle error
                    .catch(function() {
                        $scope.error = true;
                        $scope.errorMessage = "Invalid username and/or password";
                        $scope.disabled = false;
                        $scope.loginForm = {};
                    });

            };

        }
    ])
    .controller('logoutController', ['$scope', '$location', 'AuthService',
        function($scope, $location, AuthService) {

            $scope.logout = function() {

                // call logout from service
                AuthService.logout()
                    .then(function() {
                        $location.path('/login');
                    });

            };

        }
    ])
    .controller('adminlistuserController', ['$scope', '$location', 'AuthService',
        function($scope, $location, AuthService) {
            $scope.adduser_state = false;
            $scope.adduser_toggle = function() {
                $scope.adduser_state = !$scope.adduser_state;
            };
            var pageSize = $scope.pageSize = 10;
            $scope.itemsPerPage = pageSize;

            initController();

            function initController() {
                AuthService.getUserStatus()
                    .then(function() {
                        $scope.user = AuthService.getUser();
                        AuthService.listUsers()
                            .then(function(data) {
                                $scope.users = data.users;

                            })
                            // handle error
                            .catch(function() {
                                $scope.error = true;
                                $scope.errorMessage = "Something went wrong!";
                            });
                    })
            }


            $scope.link_toggle = function(index) {
                $scope.users[index]['show_deck'] = !$scope.users[index]['show_deck'];
            };
            $scope.addUser = function() {

                // initial values
                $scope.error = false;
                $scope.disabled = true;

                if ($scope.registerForm.limit === '' || isNaN($scope.registerForm.limit)) {
                    $scope.registerForm.limit = 3
                }

                // call register from service
                AuthService.addUser($scope.registerForm.name,
                        $scope.registerForm.password, $scope.registerForm.limit)
                    // handle success
                    .then(function(result) {
                        $scope.success = true;
                        $scope.error = false;
                        $scope.successMessage = result.msg;
                        $scope.disabled = false;
                        $scope.registerForm = {};
                        $scope.state = false;
                        initController();
                    })
                    // handle error
                    .catch(function(result) {
                        $scope.error = true;
                        $scope.errorMessage = result.msg;
                        $scope.disabled = false;
                        $scope.registerForm = {};
                    });
            };

        }
    ])
    .controller('adminpasswordController', ['$scope', '$location', 'AuthService',
        function($scope, $location, AuthService) {
            $scope.changePass = function() {
                if ($scope.passForm.newPass == $scope.passForm.oldpass) {
                    $scope.error = true;
                    $scope.errorMessage = 'New Password is equal to old password.';
                    $scope.disabled = false;
                    $scope.registerForm = {};
                    return;
                }
                if ($scope.passForm.newPass != $scope.passForm.confirm) {
                    $scope.error = true;
                    $scope.errorMessage = 'Password did not matched.';
                    $scope.disabled = false;
                    $scope.registerForm = {};
                    return;
                }
                // initial values
                $scope.error = false;
                $scope.success = false;
                $scope.disabled = true;

                AuthService.changePass(
                        $scope.passForm.oldpass, $scope.passForm.newPass
                    )
                    // handle success
                    .then(function(result) {
                        $scope.success = true;
                        $scope.successMessage = result.msg;
                        $scope.disabled = false;
                        $scope.registerForm = {};
                    })
                    // handle error
                    .catch(function(result) {
                        $scope.error = true;
                        $scope.errorMessage = result.msg;
                        $scope.disabled = false;
                        $scope.registerForm = {};
                    });

            };
        }
    ])
    .controller('profileController', ['$scope', '$routeParams', '$location', 'AuthService', '$uibModal', '$log',
        function($scope, $routeParams, $location, AuthService, $uibModal, $log) {

            $scope.state = false;
            $scope.toggle = function() {
                $scope.state = !$scope.state;
            };
            $scope.Math = window.Math;
            $scope.accountId = $routeParams.id;
            initController();

            function initController() {
                AuthService.getUserStatus()
                    .then(function() {
                        $scope.user = AuthService.getUser();
                    })
                    .catch(function() {
                        $scope.error = true;
                        $scope.errorMessage = "Something went wrong!";
                    });
                AuthService.getAccountById($scope.accountId)
                    .then(function(account) {
                        $scope.account = account;
                    })
                    .catch(function() {
                        $scope.error = true;
                        $scope.errorMessage = "Something went wrong!";
                    });
                AuthService.getFollowSchedules($scope.accountId)
                    .then(function(result) {
                        $scope.follow_schedules = result.schedules;
                    })
                    .catch(function(result) {
                        $scope.error = true;
                        $scope.errorMessage = result.msg;
                    });
                AuthService.getUnFollowSchedules($scope.accountId)
                    .then(function(result) {
                        $scope.unfollow_schedules = result.schedules;
                    })
                    .catch(function(result) {
                        $scope.error = true;
                        $scope.errorMessage = result.msg;
                    });
                AuthService.getLists($scope.accountId)
                    .then(function(result) {
                        $scope.lists = result.lists;
                    })
                    .catch(function(result) {
                        $scope.error = true;
                        $scope.errorMessage = result.msg;
                    });
            }
            $scope.changeFollowScheduleStatus = function() {
                AuthService.changeFollowScheduleStatus($scope.accountId, $scope.account.follow_schedule_status)
                    .then(function(result) {
                        $scope.success = true;
                        $scope.successMessage = result.msg;
                        initController();
                    })
                    .catch(function(result) {
                        $scope.error = true;
                        $scope.errorMessage = result.msg;
                        initController();
                    });
            }
            $scope.changeUnFollowScheduleStatus = function() {
                AuthService.changeUnFollowScheduleStatus($scope.accountId, $scope.account.unfollow_schedule_status, $scope.account.unfollow_schedule_option)
                    .then(function(result) {
                        $scope.success = true;
                        $scope.successMessage = result.msg;
                    })
                    .catch(function(result) {
                        $scope.error = true;
                        $scope.errorMessage = result.msg;
                    });
            }
            $scope.delList = function(id) {
                AuthService.delList(id)
                    .then(function(result) {
                        $scope.success = true;
                        $scope.successMessage = result.msg;
                        initController();
                    })
                    .catch(function(result) {
                        $scope.error = true;
                        $scope.errorMessage = result.msg;
                    });
            }
            $scope.delFollowSchedule = function(id) {
                AuthService.delFollowSchedule(id)
                    .then(function(result) {
                        $scope.success = true;
                        $scope.successMessage = result.msg;
                        initController();
                    })
                    .catch(function(result) {
                        $scope.error = true;
                        $scope.errorMessage = result.msg;

                    });
            }
            $scope.delUnFollowSchedule = function(id) {
                AuthService.delUnFollowSchedule(id)
                    .then(function(result) {
                        $scope.success = true;
                        $scope.successMessage = result.msg;
                        initController();
                    })
                    .catch(function(result) {
                        $scope.error = true;
                        $scope.errorMessage = result.msg;
                    });
            }
            $scope.openFollowSchedule = function() {
                var modalInstance = $uibModal.open({
                    animation: false,
                    ariaLabelledBy: 'modal-title-bottom',
                    ariaDescribedBy: 'modal-body-bottom',
                    templateUrl: '/static/partials/user/modal/addFollowSchedule.html',
                    size: 'lg',
                    resolve: {
                        accountId: function() {
                            return $scope.accountId;
                        }
                    },
                    controller: function($scope, $uibModalInstance, AuthService, accountId) {
                        $scope.today = function() {
                            $scope.startDate = new Date();
                        };
                        $scope.today();
                        $scope.opened = false;

                        $scope.dateOptions = {
                            dateDisabled: false,
                            formatYear: 'yy',
                            maxDate: new Date(2020, 5, 22),
                            minDate: new Date(),
                            startingDay: 1
                        };
                        $scope.openDatePicker = function() {
                            $scope.opened = true;
                        };
                        // Disable weekend selection
                        function disabled(data) {
                            var date = data.date,
                                mode = data.mode;
                            return mode === 'day' && (date.getDay() === 0 || date.getDay() === 6);
                        }


                        $scope.starttime = new Date();
                        $scope.starttime.setSeconds(0, 0);
                        $scope.endtime = new Date();
                        $scope.endtime.setHours($scope.starttime.getHours() + 4);
                        $scope.endtime.setSeconds(0, 0);

                        $scope.cancel = function() {
                            $uibModalInstance.dismiss('cancel');
                        };

                        function isNumeric(n) {
                            return !isNaN(parseInt(n));
                        }

                        $scope.addFollowSchedule = function() {
                            if ($scope.maxFollows == '' || $scope.maxFollows == undefined)
                                $scope.maxFollows = 999
                            if (!isNumeric($scope.maxFollows) || parseInt($scope.maxFollows) < 1 || parseInt($scope.maxFollows) > 1000) {
                                $scope.error = true;
                                $scope.errorMessage = 'Max Follows must to be Integer and range is 1~999.';
                                $scope.disabled = false;
                                return;
                            }

                            var starttime = $scope.starttime;
                            var endtime = $scope.endtime;
                            var maxFollows = parseInt($scope.maxFollows);

                            AuthService.addFollowSchedule(accountId, starttime, endtime, maxFollows)
                                .then(function(result) {
                                    var rs = {};
                                    rs.success = true;
                                    rs.successMessage = result.msg;
                                    $uibModalInstance.close(rs);
                                })
                                // handle error
                                .catch(function(result) {
                                    var rs = {};
                                    rs.error = true;
                                    rs.errorMessage = result.msg;
                                    $uibModalInstance.close(rs);
                                });
                        }
                    }
                });
                modalInstance.result.then(function(rs) {
                    if (rs.success) {
                        $scope.success = rs.success;
                        $scope.successMessage = rs.successMessage;
                        initController();
                    } else {
                        $scope.error = rs.error;
                        $scope.errorMessage = rs.errorMessage;
                    }
                }, function() {
                    $log.info('modal-component dismissed at: ' + new Date());
                });
            };
            $scope.openUnFollowSchedule = function() {
                var modalInstance = $uibModal.open({
                    animation: false,
                    ariaLabelledBy: 'modal-title-bottom',
                    ariaDescribedBy: 'modal-body-bottom',
                    templateUrl: '/static/partials/user/modal/addUnFollowSchedule.html',
                    size: 'lg',
                    resolve: {
                        accountId: function() {
                            return $scope.accountId;
                        }
                    },
                    controller: function($scope, $uibModalInstance, AuthService, accountId) {
                        $scope.today = function() {
                            $scope.startDate = new Date();
                        };
                        $scope.today();
                        $scope.opened = false;

                        $scope.dateOptions = {
                            dateDisabled: false,
                            formatYear: 'yy',
                            maxDate: new Date(2020, 5, 22),
                            minDate: new Date(),
                            startingDay: 1
                        };
                        $scope.openDatePicker = function() {
                            $scope.opened = true;
                        };
                        // Disable weekend selection
                        function disabled(data) {
                            var date = data.date,
                                mode = data.mode;
                            return mode === 'day' && (date.getDay() === 0 || date.getDay() === 6);
                        }


                        $scope.starttime = new Date();
                        $scope.starttime.setSeconds(0, 0);
                        $scope.endtime = new Date();
                        $scope.endtime.setHours($scope.starttime.getHours() + 4);
                        $scope.endtime.setSeconds(0, 0);
                        $scope.option = 0;
                        $scope.cancel = function() {
                            $uibModalInstance.dismiss('cancel');
                        };

                        function isNumeric(n) {
                            return !isNaN(parseInt(n));
                        }

                        $scope.addUnFollowSchedule = function() {
                            if ($scope.maxUnFollows == '' || $scope.maxUnFollows == undefined)
                                $scope.maxUnFollows = 999
                            if (!isNumeric($scope.maxUnFollows) || parseInt($scope.maxUnFollows) < 1 || parseInt($scope.maxUnFollows) > 1000) {
                                $scope.error = true;
                                $scope.errorMessage = 'Max UnFollows must to be Integer and range is 1~999.';
                                $scope.disabled = false;
                                return;
                            }

                            var starttime = $scope.starttime;
                            var endtime = $scope.endtime;
                            var maxUnFollows = parseInt($scope.maxUnFollows);
                            var option = $scope.option;

                            AuthService.addUnFollowSchedule(accountId, starttime, endtime, maxUnFollows, option)
                                .then(function(result) {
                                    var rs = {};
                                    rs.success = true;
                                    rs.successMessage = result.msg;
                                    $uibModalInstance.close(rs);
                                })
                                // handle error
                                .catch(function(result) {
                                    var rs = {};
                                    rs.error = true;
                                    rs.errorMessage = result.msg;
                                    $uibModalInstance.close(rs);
                                });
                        }
                    }
                });
                modalInstance.result.then(function(rs) {
                    if (rs.success) {
                        $scope.success = rs.success;
                        $scope.successMessage = rs.successMessage;
                        initController();
                    } else {
                        $scope.error = rs.error;
                        $scope.errorMessage = rs.errorMessage;
                    }
                }, function() {
                    $log.info('modal-component dismissed at: ' + new Date());
                });
            };
            /*
            $scope.openUploadList = function () {
                var modalInstance = $uibModal.open({
                    animation: false,
                    ariaLabelledBy: 'modal-title-bottom',
                    ariaDescribedBy: 'modal-body-bottom',
                    templateUrl: '/static/partials/user/modal/addCSVUploadList.html',
                    size: 'lg',
                    resolve: {
                        accountId: function () {
                            return $scope.accountId;
                        }
                    },
                    controller: function ($scope, $uibModalInstance, AuthService, accountId) {
                        $scope.cancel = function () {
                            $uibModalInstance.dismiss('cancel');
                        };
                        $scope.uploadList = function () {
                            AuthService.uploadList(accountId, $scope.listname, $scope.listfile)
                                .then(function (result) {
                                    var rs = {};
                                    rs.success = true;
                                    rs.successMessage = result.msg;
                                    $uibModalInstance.close(rs);
                                })
                                // handle error
                                .catch(function (result) {
                                    var rs = {};
                                    rs.error = true;
                                    rs.errorMessage = result.msg;
                                    $uibModalInstance.close(rs);
                                });
                        }
                    }
                });
                modalInstance.result.then(function (rs) {
                    if (rs.success) {
                        $scope.success = rs.success;
                        $scope.successMessage = rs.successMessage;
                        initController();
                    }
                    else {
                        $scope.error = rs.error;
                        $scope.errorMessage = rs.errorMessage;
                    }
                }, function () {
                    $log.info('modal-component dismissed at: ' + new Date());
                });
            };
            */
            $scope.openUploadList = function() {
                var modalInstance = $uibModal.open({
                    animation: false,
                    ariaLabelledBy: 'modal-title-bottom',
                    ariaDescribedBy: 'modal-body-bottom',
                    templateUrl: '/static/partials/user/modal/addUploadList.html',
                    size: 'lg',
                    resolve: {
                        accountId: function() {
                            return $scope.accountId;
                        }
                    },
                    controller: function($scope, $uibModalInstance, AuthService, accountId) {
                        $scope.cancel = function() {
                            $uibModalInstance.dismiss('cancel');
                        };
                        $scope.followings_count = $scope.followers_count = $scope.likes_count = $scope.tweets_count = 0;

                        $scope.findUser = function() {
                            followings_count = parseInt($scope.followings_count);
                            followers_count = parseInt($scope.followers_count);
                            likes_count = parseInt($scope.likes_count);
                            tweets_count = parseInt($scope.tweets_count);
                            AuthService.getListUsersByName($scope.searchText, $scope.followings_count, $scope.followers_count, $scope.likes_count, $scope.tweets_count)
                                .then(function(result) {
                                    $scope.linkedUsers = result.users;
                                })
                                // handle error
                                .catch(function(result) {
                                    console.log(result);
                                });

                        }

                        $scope.uploadCSVList = function() {
                            AuthService.uploadCSVList(accountId, $scope.listname, $scope.listfile)
                                .then(function(result) {
                                    var rs = {};
                                    rs.success = true;
                                    rs.successMessage = result.msg;
                                    $uibModalInstance.close(rs);
                                })
                                // handle error
                                .catch(function(result) {
                                    var rs = {};
                                    rs.error = true;
                                    rs.errorMessage = result.msg;
                                    $uibModalInstance.close(rs);
                                });
                        }
                        $scope.uploadList = function() {
                            AuthService.uploadList(accountId, $scope.listname, $scope.users)
                                .then(function(result) {
                                    var rs = {};
                                    rs.success = true;
                                    rs.successMessage = result.msg;
                                    $uibModalInstance.close(rs);
                                })
                                // handle error
                                .catch(function(result) {
                                    var rs = {};
                                    rs.error = true;
                                    rs.errorMessage = result.msg;
                                    $uibModalInstance.close(rs);
                                });
                        }
                    }
                });
                modalInstance.result.then(function(rs) {
                    if (rs.success) {
                        $scope.success = rs.success;
                        $scope.successMessage = rs.successMessage;
                        initController();
                    } else {
                        $scope.error = rs.error;
                        $scope.errorMessage = rs.errorMessage;
                    }
                }, function() {
                    $log.info('modal-component dismissed at: ' + new Date());
                });
            };
        }
    ])
    .controller('accountController', ['$scope', '$routeParams', '$location', 'AuthService',
        function($scope, $routeParams, $location, AuthService) {

            $scope.state = false;
            $scope.toggle = function() {
                $scope.state = !$scope.state;
            };
            initController();

            function initController() {
                AuthService.getUserStatus()
                    .then(function() {
                        $scope.user = AuthService.getUser();
                        AuthService.getAccountsByUserId($scope.user.id)
                            .then(function(accounts) {
                                $scope.accounts = accounts
                            })
                            // handle error
                            .catch(function() {
                                $scope.error = true;
                                $scope.errorMessage = "Something went wrong!";
                            });

                    });
            }

            $scope.addAccount = function() {
                if ($scope.user.account_limit > $scope.accounts.length)
                    location.href = "/user/addAccount?userid=" + $scope.user.id;
                else {
                    $scope.error = true;
                    $scope.errorMessage = "You have reached limit of accounts";
                }
            }
            $scope.delAccount = function(accountId) {
                AuthService.delAccount(accountId)
                    .then(function(result) {
                        $scope.success = true;
                        $scope.successMessage = result.msg;
                        initController();
                    })
                    // handle error
                    .catch(function(result) {
                        $scope.error = true;
                        $scope.errorMessage = result.msg;

                    });

            }
            $scope.openPools = function(accountId) {
                $location.path("/profile/" + accountId);
            }
        }
    ])
    .filter('thousandSuffix', function() {
        return function(input) {
            var exp, rounded,
                suffixes = ['K', 'M', 'G', 'T', 'P', 'E'];

            if (window.isNaN(input)) {
                return null;
            }

            if (input < 10000) {
                return input;
            }

            exp = Math.floor(Math.log(input) / Math.log(1000));

            rounded = (input / Math.pow(1000, exp)) + suffixes[exp - 1];
            return rounded;
        };
    })
    .directive('fileModel', ['$parse', function($parse) {
        return {
            restrict: 'A',
            link: function(scope, element, attrs) {
                var model = $parse(attrs.fileModel);
                var modelSetter = model.assign;

                element.bind('change', function() {
                    scope.filepath = angular.element(this).val();
                    scope.$apply(function() {
                        modelSetter(scope, element[0].files[0]);
                    });
                });
            }
        };
    }])
    .filter('getMax', function() {
        return function(input) {
            if (window.isNaN(input)) {
                return null;
            }

            if (input < 998) {
                return input;
            } else {
                return 'Unlimited';
            }
        }
    })
    .filter('getTime', function() {
        return function(input) {
            return moment(input).format("hh:mm A");
        }
    })
    .filter('getDate', function() {
        return function(input) {
            return moment(input).format("MM-DD-YYYY");
        }
    });