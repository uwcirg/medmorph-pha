// app theme colors
var appTheme = {
    themes: {
        light: {
            base: "#37353a",
            primary: '#314367',
            secondary: '#9ea5b5',
            accent: '#F8F8F8',
        }
    }
};
var appData = {
    theme: appTheme
};
new Vue({
    el: '#app',
    vuetify: new Vuetify(appData),
    data: function() {
        return {
                apiURL: "https://medmorph-pha-hapi.cirg.washington.edu/fhir/Bundle",
                postDataSource: "./Bundle.HIMSS.json",
                postURL: "https://medmorph-pha-fhir.cirg.washington.edu/fhir/$process-message",
                //apiURL: "sampleData.json", //uncomment to test
                initialized: false,
                dialog: false,
                tab: 0,
                headers: [
                    {
                        "text": "Received ("  + this.getCurrentTimeZone() + ")",
                        "value": "localDateTime",
                        "sortable": true
                    },
                    {
                        "text": "Name",
                        "value": "subject.name",
                        "sortable": true
                    },
                    {
                        "text": "DOB",
                        "value": "subject.dob",
                        "sortable": true
                    },
                    {
                        "text": "Gender",
                        "value": "subject.gender",
                        "sortable": true
                    },
                    {
                        "text": "",
                        "value": "link",
                        "align": "center",
                        "sortable": false
                    },
                ],
                resources: [],
                activeItem: {},
                alert: false,
                loading: true,
                errorMessage: "",
                maxWaitCount: 6,
                waitMessages:[
                    "Displaying all case reports",
                    "Displaying all case reports",
                    "Loading case reports ....",
                    "Loading case reports ...",
                    "Loading case reports ..",
                    "Checking for a new case reports ....."
                ],
                waitCount: 0,
                waitCountTimerId: 0
        };
    },
    mounted: function() {
        this.getData();
    },
    methods: {
        setError: function(message) {
            if (message) {
                this.errorMessage = message;
                this.alert = true;
                return;
            }
            this.alert = false;
        },
        refresh: function() {
            this.loading = true;
            var self = this;
            //post new data
            axios.get(this.postDataSource).then(function(response) {
                //console.log(" data ", response.data)
                //allow bundle to be updated each time
                response.data.identifier = [{"value": Date.now(), "system": "https://github.com/uwcirg/medmorph/counter"}];
                axios.post(self.postURL, response.data, {
                    headers: {
                      // Overwrite Axios's automatically set Content-Type
                      'Content-Type': 'application/json'
                    }
                  }).then(function(response) {
                    self.waitCount = self.maxWaitCount;
                    self.waitCountTimerId = setInterval(function() {
                        self.waitCount--;
                        if (self.waitCount <= 0) {
                            self.clearWait();
                            self.getData();
                        }
                    }, 1000);
                }).catch(function (error) {
                    // handle error
                    console.log("POST error ", error);
                    self.setError("Error when refreshing data: " + error);
                    self.clearWait();
                    self.loading = false;
                });
            });
        },
        clearWait: function() {
            this.waitCount = 0;
            clearInterval(this.waitCountTimerId);
        },
        getWaitMessage: function(index) {
            if (!this.waitMessages[index]) return "";
            return this.waitMessages[index];
        },
        getData: function() {
            var self = this;
            axios.get(this.apiURL,
                {
                    // query URL without using browser cache
                    headers: {
                      'Cache-Control': 'no-cache'
                    },
                })
            .then(function (response) {
                // handle success
                //console.log(response.data);
                if (!response || !response.data || !response.data.entry || !response.data.entry.length ) {
                    self.setError("no response data available");
                    return;
                }
                self.resources = response.data.entry.filter(function(item) {
                    return item.resource;
                }).map(function(item) {
                    return item.resource;
                });
                self.resources.forEach(function(item) {
                    item.id = Date.now() + Math.random() + Math.random() + Math.random() + Math.random();
                    item.data = item.entry ? item.entry.filter(function(item) {
                        return item.resource && item.resource.entry;
                    }).map(function(item) {
                        return item.resource.entry
                    })[0] : [];
                    item.link = "";
                    var patientResource = item.data.filter(function(d) {
                        return d.resource && d.resource.resourceType === "Patient";
                    }).map(function(o) {
                        return o.resource;
                    });
                    item.subject = {};
                    if (patientResource.length) {
                        var firstname = patientResource[0].name[0] && patientResource[0].name[0].given[0] ? patientResource[0].name[0].given[0] : "";
                        var lastname = patientResource[0].name[0] && patientResource[0].name[0].family? patientResource[0].name[0].family : "";
                        item.subject["dob"] = patientResource[0].birthDate;
                        item.subject["gender"] = patientResource[0].gender;
                        item.subject["firstname"] = firstname;
                        item.subject["lastname"] = lastname;
                        item.subject["name"] = [lastname, firstname].join(", ");
                    };
                    var timestamp = item.timestamp;
                    if (String(firstname).trim().toLowerCase() === "016-002001") {
                        timestamp = item.meta.lastUpdated;
                    }
                    item.localDateTime = self.displayDateTime(new Date(timestamp));
                    item.timestamp = self.displayDateTime(timestamp);
                });
                self.setError("");
                    //console.log("resources ", self.resources)

            })
            .catch(function (error) {
                // handle error
                console.log(error);
                self.setError(error);
            })
            .then(function () {
                // always executed
                self.initialized = true;
                setTimeout(function() {
                    self.loading = false;
                }, 250);
            });
        },
        pad: function(val, len) {
            if (!val && parseInt(val) !== 0) return "";
            val = String(val);
            len = len || 2;
            while (val.length < len) val = "0" + val;
            return val;
        },
        displayDateTime: function(timestamp) {
            if (!timestamp) return "";
            if (timestamp instanceof Date) {
                return [
                    timestamp.getFullYear(),
                    (this.pad(timestamp.getMonth()+1)),
                    this.pad(timestamp.getDate())].join("-") + " " +
                    [this.pad(timestamp.getHours()),
                    this.pad(timestamp.getMinutes()),
                    this.pad(timestamp.getSeconds()),
                    ].join(":");
            }
            timestamp = timestamp.replace(/[\T]/g, " ");
            if (timestamp.indexOf(".") !== -1) {
                timestamp = timestamp.substring(0, timestamp.indexOf("."));
            }
            return timestamp;
        },
        getCurrentTimeZone: function() {
            return new Date().toLocaleDateString(undefined, {day:"2-digit",timeZoneName: "short" }).substring(4);
        },
        handleDialogClose: function() {
            this.tab = 0;
            this.dialog = false;
            this.activeItem = {};
        },
        viewDetail: function(data, subject) {
            var resourceTypes = data.filter(function(item) {
                return item.resource && item.resource.resourceType;
            }).map(function(item) {
                return item.resource.resourceType;
            }).sort(function(a, b) {
                return a.localeCompare(b);
            }).filter( function( item, index, inputArray ) {
                return inputArray.indexOf(item) === index;
            }).map(function(item, index) {
                var resourceData = data.filter(function(o) {
                    return o.resource && (o.resource.resourceType === item) && (o.resource.text && o.resource.text.div)
                });
                return {
                    "name": item,
                    "sortIndex": item.toLowerCase() === "patient" ? -1 : index,
                    "count": resourceData.length,
                    "data": resourceData.map(function(o) {
                        return o.resource.text.div
                    })
                }
            }).sort(function(a, b) {
                return (a.sortIndex - b.sortIndex);
            });
            //console.log("resources types ", resourceTypes)
            this.activeItem.resourceTypes = resourceTypes;
            this.activeItem.subject = subject;
            this.tab = 0;
            this.dialog = true;
        }
    }
});
