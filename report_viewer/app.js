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
                apiURL: "https://medmorph-pha-fhir.cirg.washington.edu/fhir/Bundle",
                //apiURL: "sampleData.json", //uncomment to test
                initialized: false,
                dialog: false,
                tab: 0,
                headers: [
                    {
                        "text": "Received",
                        "value": "timestamp",
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
                errorMessage: ""
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
            this.getData();
        },
        getData: function() {
            var self = this;
            axios.get(this.apiURL, {
                // query URL without using browser cache
                headers: {
                  'Cache-Control': 'no-cache',
                  'Pragma': 'no-cache',
                  'Expires': '0',
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
                    item.timestamp = self.displayDateTime(item.timestamp);
                    var patientResource = item.data.filter(function(d) {
                        return d.resource.resourceType === "Patient";
                    }).map(function(o) {
                        return o.resource;
                    });
                    item.subject = {};
                    if (patientResource.length) {
                        item.subject["dob"] = patientResource[0].birthDate;
                        item.subject["gender"] = patientResource[0].gender;
                        item.subject["name"] = patientResource[0].name[0].text;
                    };
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
        displayDateTime: function(timestamp) {
            if (!timestamp) return "";
            timestamp = timestamp.replace(/[\T]/g, " ");
            if (timestamp.indexOf(".") !== -1) {
                timestamp = timestamp.substring(0, timestamp.indexOf("."));
            }
            return timestamp;
        },
        handleDialogClose: function() {
            this.tab = 0;
            this.dialog = false;
        },
        viewDetail: function(data, subject) {
            var resourceTypes = data.map(function(item) {
                return item.resource.resourceType;
            }).filter( function( item, index, inputArray ) {
                return inputArray.indexOf(item) === index;
            });
            resourceTypes = resourceTypes.map(function(item) {
                var resourceData = data.filter(function(o) {
                    return (o.resource.resourceType === item) && (o.resource.text && o.resource.text.div)
                });
                return {
                    "name": item,
                    "count": resourceData.length,
                    "data": resourceData.map(function(o) {
                        return o.resource.text.div
                    })
                }
            });
            this.activeItem.resourceTypes = resourceTypes.sort(function(a, b) {
                if (a.name.toLowerCase() === "patient") return -1;
                if (a.name < b.name) return -1;
                if (a.name > b.name) return 1;
                return 0;
            });
            this.activeItem.subject = subject;
            this.tab = 0;
            this.dialog = true;
        }
    }
});
