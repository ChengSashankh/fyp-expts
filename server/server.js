const express = require('express');
const path = require('path');
const SearchModule = require('./search');

const app = express();
const searchModule = new SearchModule();

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

// TODO: Mode not implemented. Perform OR search by default
app.get('/query/:context_string/:equation_string/:mode', (req, res) => {
    const { context_string, equation_string, mode } = req.params;
    let results = {
        matches: searchModule.search(context_string, equation_string)
    };

    res.json(results);
});

const port = 3000;
app.listen(port, () => {
    console.log('Listening at port: ', port);
});