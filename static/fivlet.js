document.addEventListener('DOMContentLoaded', function(){

    // Creating a variable to keep track of rows
    let currentRow = 0;
    // Creating a fixed variable for the number of rows
    const maxRows = 5;

    // Selecting the message are where the result will be shown on the page
    let result_message = document.querySelector('#result_message');
    let message = result_message.querySelector('#message');
    let fivlet = result_message.querySelector('#fivlet strong');
    let button = result_message.querySelector('button');

    // A FUNCTION that will behave accordingly: 
    // focus will automatically shift to the next box if the current box is filled with an input
    // also backspace will erase the current box and move the focus to the previous one
    function autoFocusCols(rowNumber) {

        // Selecting one row
        let row = document.querySelector(`div[data-row='${rowNumber}']`);
        // Selecting all the boxes inside that row
        const inputs = row.querySelectorAll('input[data-col]');

        // Enabling each box the current row
        inputs.forEach(function(box) {
            box.disabled = false;
        });

        // For each set of 5 boxes (for each row)
        inputs.forEach(function(box, index) {
            
            // Moving the focus to the next box if the present one is filled
            box.addEventListener('input', function(e) {
                if (this.value.length === 1 && index < inputs.length - 1) {
                    inputs[index + 1].focus();
                }
                else if (index === inputs.length - 1) {
                    // Preventing the focus to move to the first box of the next row
                    // after the last box of the present row
                    e.preventDefault();
                }
            });

            // Moving the focus to the previous box if the present one's value is erased using backspace
            box.addEventListener('keydown', function(k){
                if (k.key === 'Backspace' && !this.value && index > 0) {
                    inputs[index - 1].focus();
                }
            });
        });

        // By default the first box of the rowNumber will be focused.
        // This is not written at the beginning because inputs and boxes and row indexes are not chosen yet.
        inputs[0].focus();        

        // Disable other rows
        let otherRows = document.querySelectorAll('div[data-row]');
        otherRows.forEach(function(row, i) {
            if (i !== rowNumber) {
                // Selecting the boxes of other rows
                let otherBoxes = row.querySelectorAll('input')
                otherBoxes.forEach(function(box) {
                    box.disabled = true;
                });
            }
        });
    }

    // A FUNCTION that will join the letters and create the five letter word guessed by the user
    function createWord(rowNumber) {

        // Getting the current row from the DOM
        let row = document.querySelector(`div[data-row='${rowNumber}']`);
        // Getting the letters from that row
        const boxes = row.querySelectorAll('input[data-col]');

        // Joining the letters into a word
        let word = Array.from(boxes).map(function(box) {
            return box.value.toUpperCase()
        }).join('');

        return word;      
    }

    // A FUNCTION that updates the GUI based on the result
    function showResult (rowNumber, resultDictionary) {
        let row = document.querySelector(`div[data-row='${rowNumber}']`);
        let boxes = row.querySelectorAll('input[data-col]');
        
        for (let i = 0; i < boxes.length; i++) {
            boxes[i].style.backgroundColor = resultDictionary.colors[i];
            if (resultDictionary.type === "win") {
                boxes[i].style.color = 'white';
            }
        }
    }

    // A FUNCTION that will disable all boxes after the game is over
    function disableAll() {
        let boxes = document.querySelectorAll('input')

        for (let i = 0; i < boxes.length; i++) {
            boxes[i].disabled = true;
        }
    } 

    // Using the autoFocusCols for each row (currentRow will be incremented later)
    autoFocusCols(currentRow);

    // Get the submit button
    let submit = document.getElementById('submit');
    submit.addEventListener('click', async function() {
        // Getting the word from DOM using createWord function
        let word = createWord(currentRow);

        if (word.length !== 5 ) {
            alert("Word must have five letter. The game is fiv + let");
            return;
        }
       
        // Sending the word to the backend server for validation
        let response = await fetch('/validation', {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({word: word, row: currentRow})
        });

        // Waiting for the result of validation from the backend server
        let result = await response.json();

        // If the given word does not exist in the dictionary
        if (!result) {
            alert("Word does not exist");
            return;
        }


        showResult(currentRow, result);

        if (result.type === "win") {
            message.textContent = 'Congratulations!';
            button.textContent = 'Guess Again';
            disableAll();
            return;
        }
        else if (result.type === "lost") {
            message.textContent = 'Better Luck Next Time!';
            fivlet.textContent = `Word: ${result.word}`;
            button.textContent = 'Try Again';
            disableAll();
            return;
        }
        else {
            // After submitting the current word (row), if (attempts not exhausted) {move to the next row}    
            if (currentRow < maxRows - 1) {
                currentRow++;
                autoFocusCols(currentRow);
            }

            // Selecting the 26 letters below the table
            let unusedLetters = document.querySelectorAll('#unused_letters div');

            // Iterating over the 'colors' key in result dictionary
            for (let i = 0; i < result.colors.length; i++) {
                
                // If the current position color is grey
                if (result.colors[i] === "grey") {
                    
                    // Using forEach function to access each item inside unusedLetters nodelist
                    unusedLetters.forEach(function(letter) {

                        // If the letter matches with the guessed word's letter
                        if (letter.textContent === word[i]) {
                            letter.style.backgroundColor = 'grey';
                            letter.style.color = 'white';
                        }
                    });
                }
            }
        }


    });

    // Revealing the actual fivlet word if the user gives up 
    let reveal = document.getElementById('reveal');
    reveal.addEventListener('click', async function() {

        // Sending request to the backend for the actual word and info about number attemps (if any)
        let response = await fetch('/reveal', {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({row: currentRow}) // Numer of attemps (if any or 0)
        });

        let result = await response.json()

        message.textContent = 'Gave up too easily?';
        fivlet.textContent = `Word: ${result.word}`;
        button.textContent = 'Try Another';
        disableAll();
        return;
    });

    // Clearing the whole row if the user clicks the 'clear' button
    let clear = document.getElementById('clear');
    clear.addEventListener('click', function() {
        let row = document.querySelector(`div[data-row='${currentRow}']`);
        let boxes = row.querySelectorAll('input[data-col]');

        for (let i = 0; i < boxes.length; i++) {
            boxes[i].value = '';
        }
        boxes[0].focus();
    });
});