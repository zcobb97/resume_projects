var main = function () {

    //On page load, look for session cookie, and verify its authenticity
    //If there IS a session cookie, and its bad, set the login message to session expired
    //Note that we assume only one cookie for this domain
    let sessionId = document.cookie.split(';')[0].split("=")[1];

    //No sessionId
    if(sessionId == null) {
        $("#showLoginModalButton").click();
    } else {

        //We have a session ID, validate it with the introspect
        let results = $.ajax({
            url: "/introspect",
            async: false
        }).responseText;

        if(results != "GOOD"){
            $("#loginMessage").empty();
            $("#showLoginModalButton").click();
            document.cookie = "";
        } else {
            $("#dismissLoginModalButton").click();
            populateNavPanel();
        }

    }

    document.getElementById("loginSubmitButton").onclick = submitLogin;

    function submitLogin() {

        let username = document.getElementById("usernameInput").value;
        let password = document.getElementById("passwordInput").value;

        var sessionIdRet = $.ajax({
            url: "/login?username=" + username + "&password=" + password,
            async: false
        }).responseText;

        if(sessionIdRet != null && sessionIdRet != "") {

            //Successful login ... set session ID and clean up
            document.cookie = "sessionId="+sessionIdRet+"; Path=/; Expires=Sat, 31 Dec 2050 00:00:01 GMT;"
            document.getElementById("usernameInput").value = "";
            document.getElementById("passwordInput").value = "";
            $("#dismissLoginModalButton").click();
            $("#loginMessage").empty();
            populateNavPanel();

            //document.cookie.split(';')[0].split("=")[1]
        } else {
            $("#loginMessage").empty();
            var newdiv1 = $( "<div id='loginMessageText' class='redText' >Invalid login</div>" );
            $("#loginMessage").append(newdiv1);

        }

    };

    function populateNavPanel(){

        var welcomeMessage = $.ajax({
            url: "/getWelcomeMessage",
            async: false
        }).responseText;

        var userType = $.ajax({
            url: "/getUserType",
            async: false
        }).responseText;

        if(userType == "provider"){
            document.getElementById("newUserButtonDiv").classList.remove("hiddenSection");
            document.getElementById("selectPatientButtonDiv").classList.remove("hiddenSection");
            document.getElementById("intakeCalendarButtonDiv").classList.remove("hiddenSection");
            document.getElementById("addAppointmentButtonDiv").classList.remove("hiddenSection");
            document.getElementById("createEmployeeButtonDiv").classList.remove("hiddenSection");
        } else {
            document.getElementById("newUserButtonDiv").classList.add("hiddenSection");
            document.getElementById("selectPatientButtonDiv").classList.add("hiddenSection");
            document.getElementById("intakeCalendarButtonDiv").classList.add("hiddenSection");
            document.getElementById("addAppointmentButtonDiv").classList.add("hiddenSection");
            document.getElementById("createEmployeeButtonDiv").classList.add("hiddenSection");
        }

        if(welcomeMessage != "Select Patient To Proceed"){
            document.getElementById("insuranceButton").classList.remove("disabled");
            //document.getElementById("ordersButton").classList.remove("disabled");
            document.getElementById("patientInformationButton").classList.remove("disabled");
            document.getElementById("patientHistoryButton").classList.remove("disabled");
            document.getElementById("messagingButton").classList.remove("disabled");
        }

        document.getElementById("navPanelUserWelcome").innerHTML = welcomeMessage;



    }


}

$(document).ready(main);


function logout(){
    document.cookie = "; Path=/; Expires=Sat, 31 Dec 2000 00:00:01 GMT;"

    var logoutResults = $.ajax({
        url: "/logout",
        async: false
    }).responseText;

}


var sectionList = ["mainPage","resume","contact","portfolio"];

//var myModal = new bootstrap.Modal(document.getElementById('exampleModal'), {});

function navigateClaims(insuranceId){

    alert("This will navigate to the claims window with a filter on which claims are displayed");

window.location.href="claims.html?insuranceId=" + insuranceId;


}

function orderNavPanelButtonClick(){

    document.getElementById("mainContent").src="ordersPatient.html";

}


function clearFilters(){

    alert("This will clear any filters on the data");


}

function selectPatientNavPanelButtonClick(){

    alert("this will allow a provider to search for and select a particular patient. once selected the patientId is pushed to the session object in back end");
    document.getElementById("mainContent").src="patientSelect.html";

}

function insuranceNavPanelButtonClick(){

    document.getElementById("mainContent").src="insurance.html";
}

function claimsNavPanelButtonClick(){

    document.getElementById("mainContent").src="claims.html";
}

function patientHistoryNavPanelButtonClick(){

    document.getElementById("mainContent").src="patientHistory.html";
}

function insurance1buttonClick(){
  //BSL TODO maybe here we have a service that gets the contents of the div and replaces the existing row instead of revealing a div
  //THEN, the save will return it to normal using a different service
  //That would be consistent with the loading of the data as well

  document.getElementById("insurance1div").classList.remove("hiddenSection");
  document.getElementById("insurance1Editdiv").classList.remove("hiddenSection");

  document.getElementById("insurance2div").classList.add("hiddenSection");
  document.getElementById("insurance2div").classList.remove("row");
  document.getElementById("insurance3div").classList.add("hiddenSection");
  document.getElementById("insurance3div").classList.remove("row");
  document.getElementById("insuranceAddButtondiv").classList.add("hiddenSection");
  document.getElementById("insuranceAddButtondiv").classList.remove("row");



  //document.getElementById("insurance2Editdiv").classList.add("hiddenSection");

}

function insuranceAddClearButtonClick(){
  document.getElementById("addType").value="";
  document.getElementById("addProvider").value="";
  document.getElementById("addGroup").value="";

}

function insuranceAddSaveButtonClick(){


reloadPageClick();
  //document.getElementById("insurance1div").classList.remove("hiddenSection");

}

function insuranceAddbuttonClick(){


  document.getElementById("insuranceAddSavediv").classList.remove("hiddenSection");
  document.getElementById("insuranceAddButtondiv").classList.add("hiddenSection");


}

function reloadPageClick(){
  alert("use web service to save then use another to refresh contents or have web service return an object");

location.reload();
  //window.reloadPage();
  return false;

}



function claim1DetailsbuttonClick(){

    myModal.show();


}









function showSection(sectionName){

    var i;
    for(i=0;i < sectionList.length;i++){
        //alert(sectionList[i] + "Link");
        document.getElementById(sectionList[i]).classList.remove("visibleSection");
        document.getElementById(sectionList[i]).classList.add("hiddenSection");

        document.getElementById(sectionList[i] + 'Link').classList.remove("activeLink");
        document.getElementById(sectionList[i] + 'Link').classList.add("inactiveLink");

    }

    document.getElementById(sectionName).classList.add("visibleSection");
    document.getElementById(sectionName + 'Link').classList.remove("inactiveLink");
    document.getElementById(sectionName + 'Link').classList.add("activeLink");


}

function contactSubmit(){

    let subject = document.getElementById("contactSubject").value;
    let message = document.getElementById("contactMessage").value;

    alert("Your message:" + message + " has been submitted with subject " + subject);

    document.getElementById("contactSubject").value = "";
    document.getElementById("contactMessage").value = "";

    document.getElementById("submitButton").classList.add("disabledInput");


}

function activateSubmit(){

    document.getElementById("submitButton").classList.remove("disabledInput");

}

function revealEmail(){

    const builtEmailAddyStart = "le" + "a" + "rb@";
    const builtEmailAddyEnd = "u" + "a" + "b." + "edu";



    document.getElementById("emailAddress").innerText=builtEmailAddyStart + builtEmailAddyEnd;

}
