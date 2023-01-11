

class BoggleGame {
    /* make a new game at this DOM id */
  
    constructor(boardId, secs = 180) {
        this.secs = secs; // game length
        this.showTimer();
      
        this.score = 0;
        this.words = new Set();
        this.board = $("#" + boardId);
        this.input = $("#word");
        this.tbody = $("tbody");
        this.input_value = ""
    
        // every sec, "tick"
        this.timer = setInterval(this.tick.bind(this), 1000);
    
        $(".add-word", this.board).on("submit", this.handleSubmit.bind(this));
        $("tbody", this.board).on("click", this.handleClick.bind(this));
       
    }
  
    /* show word in list of words */
  
    showWord(word) {
      $(".words", this.board).append(`${word} - `);
    }
  
    /* show score in html */
  
    showScore() {
      $(".score", this.board).text(this.score);
    }
  
    /* show a status message */
  
    showMessage(msg, cls) {
      $(".msg", this.board)
        .text(msg)
        .removeClass()
        .addClass(`msg ${cls}`);
    }
  
    /* handle submission of word: if unique and valid, score & show */
  
    async handleSubmit(evt) {
        evt.preventDefault();
        const $word = $(".word", this.board);
        
        let word = $word.val().trim();
    
        if (!word) return;
    
        if (this.words.has(word.toLowerCase())) {
            this.showMessage(`Already found ${word}`, "err");
            this.input_value = "";
            $("#word").val(this.input_value);
            $("div").removeClass("selected");
            $word.val("").focus();
            return;
        }
    
        // check server for validity
        const resp = await axios.get("/guess", { params: { word: word }});
        if (resp.data.result === "not-a-valid-word") {
            this.showMessage(`${word} is not a valid Boggle word`, "err");
        } else if (resp.data.result === "not-found-on-board") {
            this.showMessage(`${word} is not found on this board`, "err");
        } else {
            let this_score = Math.ceil((word.length-1)*(word.length-1)/3);
            this.showWord(`${word} : ${this_score}`);
            this.score += this_score
            this.showScore();
            this.words.add(word.toLowerCase());
            this.showMessage(`Added: ${word}`, "ok");
        }
        this.input_value = "";
        $("#word").val(this.input_value);
        $("div").removeClass("selected");
        $word.val("").focus();
    }
  
    /* Update timer in DOM */
  
    showTimer() {
      $(".timer", this.board).text(this.secs);
    }
  
    /* Tick: handle a second passing in game */
  
    async tick() {
      this.secs -= 1;
      this.showTimer();
  
      if (this.secs === 0) {
        clearInterval(this.timer);
        await this.scoreGame();
      }
    }
 

    async handleClick(evt) {
        let target = evt.target;
        let targetID = target.id;
    
        this.input_value += targetID;
     
        $(evt.target).addClass("selected")
        $("#word").val(this.input_value);
    }
  
    /* end of game: score and update message. */
  
    async scoreGame() {
      $(".add-word", this.board).hide();
      const resp = await axios.post("/post-score", { score: this.score });
      if (resp.data.brokeRecord) {
        this.showMessage(`New record: ${this.score}`, "ok");
      } else {
        this.showMessage(`Final score: ${this.score}`, "ok");
      }
    }
  }