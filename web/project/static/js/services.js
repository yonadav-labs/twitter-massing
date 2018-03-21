angular.module('myApp').factory('AuthService',
    ['$q', '$timeout', '$http',
        function ($q, $timeout, $http) {

            // create user variable
            var user = null;

            // return available functions for use in controllers
            return ({
                isLoggedIn: isLoggedIn,
                login: login,
                logout: logout,
                addUser: addUser,
                getUserStatus: getUserStatus,
                getUser: getUser,
                listUsers: listUsers,
                changePass: changePass,
                getAccountsByUserId: getAccountsByUserId,
                getAccountById:getAccountById,
                getFollowSchedules: getFollowSchedules,
                addFollowSchedule: addFollowSchedule,
                delFollowSchedule: delFollowSchedule,
                getUnFollowSchedules: getUnFollowSchedules,
                addUnFollowSchedule: addUnFollowSchedule,
                delUnFollowSchedule: delUnFollowSchedule,
                uploadCSVList: uploadCSVList,
                uploadList:uploadList,
                getLists: getLists,
                delList: delList,
                delAccount:delAccount,
                changeFollowScheduleStatus:changeFollowScheduleStatus,
                changeUnFollowScheduleStatus:changeUnFollowScheduleStatus,
                getListUsersByName:getListUsersByName
            });

            function isLoggedIn() {
                if (user) {
                    return true;
                } else {
                    return false;
                }
            }

            function getUser() {
                return user;
            }
            function getListUsersByName(screen_name,followings_count, followers_count, likes_count, tweets_count) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/user/findUsers',{
                    screen_name:screen_name,
                    followings_count:followings_count,
                    followers_count:followers_count,
                    likes_count:likes_count,
                    tweets_count:tweets_count
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }
            function login(name, password) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/login', {name: name, password: password})
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result.status) {
                            user = data.result.user;
                            console.log(user);
                            deferred.resolve(user);
                        } else {
                            user = false;
                            deferred.reject();
                        }
                    })
                    // handle error
                    .error(function (data) {
                        user = false;
                        deferred.reject();
                    });

                // return promise object
                return deferred.promise;

            }

            function logout() {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a get request to the server
                $http.get('/logout')
                // handle success
                    .success(function (data) {
                        user = false;
                        deferred.resolve();
                    })
                    // handle error
                    .error(function (data) {
                        user = false;
                        deferred.reject();
                    });

                // return promise object
                return deferred.promise;

            }

            function addUser(name, password, limit) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/admin/addUser', {
                    name: name, password: password, limit:limit
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result.status > 0) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }

            function listUsers() {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/admin/listUsers', {})
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result.status > 0) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }

            function changePass(oldpass, newpass) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/admin/changePass', {
                    oldpass: oldpass, newpass: newpass
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result.status > 0) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }

            function getAccountsByUserId(userid) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/user/getAccountsByUserId', {
                    userid: userid
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }
            function getAccountById(id) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/user/getAccountById', {
                    id: id
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }
            function getFollowSchedules(accountId) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/user/getFollowSchedules', {
                    accountId: accountId
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }

            function delFollowSchedule(id) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/user/delFollowSchedule', {
                    id: id
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result.status > 0) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }

            function getUnFollowSchedules(accountId) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/user/getUnFollowSchedules', {
                    accountId: accountId
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }

            function addFollowSchedule(accountId, starttime, endtime, maxFollows) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/user/addFollowSchedule', {
                    accountId: accountId,
                    starttime: starttime,
                    endtime: endtime,
                    maxFollows: maxFollows
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result.status > 0) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }

            function delUnFollowSchedule(id) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/user/delUnFollowSchedule', {
                    id: id
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result.status > 0) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }

            function addUnFollowSchedule(accountId, starttime, endtime, maxUnFollows,option) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/user/addUnFollowSchedule', {
                    accountId: accountId,
                    starttime: starttime,
                    endtime: endtime,
                    maxUnFollows: maxUnFollows,
                    option:option
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result.status > 0) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }

            function uploadCSVList(accountId, listname, listfile) {

                // create a new instance of deferred
                var deferred = $q.defer();
                var fd = new FormData();

                fd.append('accountId', accountId);
                fd.append('file', listfile);
                fd.append('listname', listname);

                // send a post request to the server
                $http.post('/user/uploadCSVList', fd, {
                    transformRequest: angular.identity,
                    headers: {'Content-Type': undefined}
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result.status > 0) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }

            function uploadList(accountId, listname, listusers) {

                // create a new instance of deferred
                var deferred = $q.defer();
                // send a post request to the server
                $http.post('/user/uploadList', {
                    accountId:accountId,
                    listname:listname,
                    listusers:listusers
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result.status > 0) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }

            function getLists(accountId) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/user/getLists', {
                    accountId: accountId
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result.status > 0) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }

            function delList(id) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/user/delList', {
                    id: id
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }
            function delAccount(accountId) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/user/delAccount', {
                    accountId: accountId
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }
            function changeFollowScheduleStatus(accountId, follow_schedule_status) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/user/changeFollowScheduleStatus', {
                    accountId:accountId,
                    follow_schedule_status: follow_schedule_status
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }
            function changeUnFollowScheduleStatus(accountId, unfollow_schedule_status, unfollow_schedule_option) {

                // create a new instance of deferred
                var deferred = $q.defer();

                // send a post request to the server
                $http.post('/user/changeUnFollowScheduleStatus', {
                    accountId:accountId,
                    unfollow_schedule_status: unfollow_schedule_status,
                    unfollow_schedule_option:unfollow_schedule_option
                })
                // handle success
                    .success(function (data, status) {
                        if (status === 200 && data.result) {
                            deferred.resolve(data.result);
                        } else {
                            deferred.reject(data.result);
                        }
                    })
                    // handle error
                    .error(function (data) {
                        deferred.reject(data.result);
                    });

                // return promise object
                return deferred.promise;

            }
            function getUserStatus() {
                return $http.get('/status')
                // handle success
                    .success(function (data) {
                        if (data.result.status) {
                            user = data.result.user;
                        } else {
                            user = false;
                        }
                    })
                    // handle error
                    .error(function (data) {
                        user = false;
                    });
            }

        }]);