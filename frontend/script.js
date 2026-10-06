// --------------------------------------------------
// 1. DATASET COLUMNS
// --------------------------------------------------

const categoricalColumns = [

    "Cbal",
    "Chist",
    "Cpur",
    "Sbal",
    "Edur",
    "MSG",
    "Oparties",
    "Rdur",
    "Prop",
    "inPlans",
    "Htype",
    "JobType",
    "telephone",
    "foreign"

];


// --------------------------------------------------
// 2. LOAD OPTIONS
// --------------------------------------------------

async function loadOptions() {

    try {

        const response = await fetch(
            "/options"
        );


        const data = await response.json();


        if (data.error) {

            throw new Error(
                data.error
            );

        }


        categoricalColumns.forEach(
            function(column) {

                const select =
                    document.getElementById(
                        column
                    );


                const values =
                    data[column];


                values.forEach(
                    function(value) {

                        const option =
                            document.createElement(
                                "option"
                            );


                        option.value = value;

                        option.textContent = value;

                        select.appendChild(
                            option
                        );

                    }
                );

            }
        );

    }

    catch (error) {

        showError(
            "Unable to load dataset options: " +
            error.message
        );

    }

}


// --------------------------------------------------
// 3. GET FORM VALUE
// --------------------------------------------------

function getValue(id) {

    return document
        .getElementById(id)
        .value;

}


// --------------------------------------------------
// 4. SUBMIT FORM
// --------------------------------------------------

document
    .getElementById("creditForm")
    .addEventListener(
        "submit",
        async function(event) {

            event.preventDefault();


            hideError();

            hideResult();


            const button =
                document.getElementById(
                    "predictButton"
                );


            const loading =
                document.getElementById(
                    "loading"
                );


            button.disabled = true;

            loading.classList.remove(
                "hidden"
            );


            // ----------------------------------
            // COLLECT FORM DATA
            // ----------------------------------

            const data = {

                Cbal: getValue("Cbal"),

                Cdur: Number(
                    getValue("Cdur")
                ),

                Chist: getValue("Chist"),

                Cpur: getValue("Cpur"),

                Camt: Number(
                    getValue("Camt")
                ),

                Sbal: getValue("Sbal"),

                Edur: getValue("Edur"),

                InRate: Number(
                    getValue("InRate")
                ),

                MSG: getValue("MSG"),

                Oparties: getValue(
                    "Oparties"
                ),

                Rdur: getValue("Rdur"),

                Prop: getValue("Prop"),

                age: Number(
                    getValue("age")
                ),

                inPlans: getValue(
                    "inPlans"
                ),

                Htype: getValue("Htype"),

                NumCred: Number(
                    getValue("NumCred")
                ),

                JobType: getValue(
                    "JobType"
                ),

                Ndepend: Number(
                    getValue("Ndepend")
                ),

                telephone: getValue(
                    "telephone"
                ),

                foreign: getValue(
                    "foreign"
                )

            };


            try {

                // ------------------------------
                // SEND DATA TO FLASK
                // ------------------------------

                const response =
                    await fetch(
                        "/predict",
                        {

                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body:
                                JSON.stringify(
                                    data
                                )

                        }
                    );


                const result =
                    await response.json();


                if (!response.ok) {

                    throw new Error(
                        result.error ||
                        "Prediction failed."
                    );

                }


                // ------------------------------
                // DISPLAY RESULT
                // ------------------------------

                showResult(
                    result
                );

            }

            catch (error) {

                showError(
                    error.message
                );

            }

            finally {

                button.disabled = false;

                loading.classList.add(
                    "hidden"
                );

            }

        }
    );


// --------------------------------------------------
// 5. DISPLAY RESULT
// --------------------------------------------------

function showResult(result) {

    const resultBox =
        document.getElementById(
            "result"
        );


    const prediction =
        document.getElementById(
            "prediction"
        );


    const goodProbability =
        document.getElementById(
            "goodProbability"
        );


    const badProbability =
        document.getElementById(
            "badProbability"
        );


    prediction.textContent =
        "Credit Status: " +
        result.prediction;


    prediction.classList.remove(
        "good",
        "bad"
    );


    if (
        result.prediction === "Good"
    ) {

        prediction.classList.add(
            "good"
        );

    }

    else {

        prediction.classList.add(
            "bad"
        );

    }


    goodProbability.textContent =
        result.good_probability +
        "%";


    badProbability.textContent =
        result.bad_probability +
        "%";


    resultBox.classList.remove(
        "hidden"
    );


    resultBox.scrollIntoView({
        behavior: "smooth"
    });

}


// --------------------------------------------------
// 6. SHOW ERROR
// --------------------------------------------------

function showError(message) {

    const errorBox =
        document.getElementById(
            "error"
        );


    errorBox.textContent =
        message;


    errorBox.classList.remove(
        "hidden"
    );

}


// --------------------------------------------------
// 7. HIDE ERROR
// --------------------------------------------------

function hideError() {

    document
        .getElementById("error")
        .classList.add(
            "hidden"
        );

}


// --------------------------------------------------
// 8. HIDE RESULT
// --------------------------------------------------

function hideResult() {

    document
        .getElementById("result")
        .classList.add(
            "hidden"
        );

}


// --------------------------------------------------
// 9. START
// --------------------------------------------------

loadOptions();