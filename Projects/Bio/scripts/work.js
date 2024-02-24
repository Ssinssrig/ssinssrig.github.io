// Listens for the event once page is fully loaded
document.addEventListener('DOMContentLoaded', function() {

    let question1Buttons = document.querySelectorAll('#question1 .incorrect, #question1 .correct');
    let question2Buttons = document.querySelectorAll('#question2 .incorrect, #question2 .correct');
    let question3Buttons = document.querySelectorAll('#question3 .incorrect, #question3 .correct');
    let question4Buttons = document.querySelectorAll('#question4 .incorrect, #question4 .correct');

    // Resetting previously marked button if other button within the same question was marked
    function resetButtonColors(buttons) {
        buttons.forEach(btn => {
            btn.style.backgroundColor = ''; // Reset button color
            btn.style.borderColor = '';
        });
    }

    // Marking clicked button
    function handleButtonClick(buttons) {
        buttons.forEach(button => {
            button.addEventListener('click', () => {
                resetButtonColors(buttons); // Reset buttons' colors within the respective question
                button.style.backgroundColor = 'grey'; // Change clicked button's color
                button.style.borderColor = 'black';
            });
        });
    }

    handleButtonClick(question1Buttons); // Attach click event listeners for question 1 buttons
    handleButtonClick(question2Buttons); // Attach click event listeners for question 2 buttons
    handleButtonClick(question3Buttons); // Attach click event listeners for question 3 buttons
    handleButtonClick(question4Buttons); // Attach click event listeners for question 4 buttons

    let correctButtons = document.querySelectorAll('.correct');
    let incorrectButtons = document.querySelectorAll('.incorrect');
    let checkButton = document.querySelector('.check');
    let scoreCount = document.querySelectorAll('.correct');

    // Flaffing marked answers as correct or incorrect
    function validateAnswers(buttons) {
        buttons.forEach(btn => {
            if (btn.style.backgroundColor === 'grey') {
                if (btn.classList.contains('correct')) {
                    btn.style.backgroundColor = 'lightgreen';
                    btn.style.borderColor = 'black';

                } else if (btn.classList.contains('incorrect')) {
                    btn.style.backgroundColor = '#FFCCCB';
                    btn.style.borderColor = 'black';
                }
            }
        });
    }

    // Counting all correct (green) answers and returns score
    function countCorrect(buttons) {
        let score = 0;
        buttons.forEach(btn => {
            if (btn.style.backgroundColor === 'lightgreen') {
                score++;
            }
        });
        for (let i = 1; i <= 4; i++) {
            const background = document.getElementById('ba' + i).style.backgroundColor;
            const targetId = 'ab' + i;
            const targetElement = document.getElementById(targetId);

            targetElement.style.backgroundColor = (background === 'lightgreen') ? 'lightgreen' : '#FFCCCB';
        }
        return score;
    }

    // Checks if all the answers were or are marked
    function checkAllQuestionsAnswered() {
        let questions = [question1Buttons, question2Buttons, question3Buttons, question4Buttons];

        for (let i = 0; i < questions.length; i++) {
            let answered = false;
            // `in` would be used for iterating over properties of an abject
            // `of` has to be used for iterating over arrays, or strings
            for (let button of questions[i]) {
                const backgroundColor = button.style.backgroundColor;
                if (backgroundColor !== '') {
                    answered = true;
                    break;
                }
            }
            if (!answered) {
                return false; // Returns false if any question has not been answered
            }
        }
        return true; // All questions have been answered
    }

    checkButton.addEventListener('click', () => {
        if (checkAllQuestionsAnswered()) {
            // `validateAnswers` takes only one argument, but by using `...arg,` we're able to run it several times with different args
            validateAnswers([...question1Buttons, ...question2Buttons, ...question3Buttons, ...question4Buttons]);
            score = countCorrect(correctButtons);
            document.getElementById('score').innerHTML = score + "/4";
            document.getElementById('a1').innerHTML = "1. While there are many factors that can contribute to developing back pain, poor posture is the most common one. So make sure you don't slouch while sitting or standing, and keep your head straight when using your phone.";
            document.getElementById('a2').innerHTML = "2. Discopathy is the most common cause of back pain. Symptoms can range from mild to excruciating and radiate to nearly any part of the body, depending on the degree of injury and its location in the spine.";
            document.getElementById('a3').innerHTML = "3. While all of these interventions can help temporarily, unfortunately, there is no easy way to fix the cause of back pain. Proper exercises and correct posture are the keys.";
            document.getElementById('a4').innerHTML = "4. If you don't know the exact cause of your back pain, be very careful when choosing exercises or stretches. Some of them can not only worsen your symptoms but also cause further damage to your body. It's better to consult with a physical therapist.";
        } else {
            document.getElementById('a1').innerHTML = "Please answer all questions before checking your score.";
            document.getElementById('a2').innerHTML = "";
            document.getElementById('a3').innerHTML = "";
            document.getElementById('a4').innerHTML = "";
        }
    });
});
