const parse = require('csv-parse/lib/sync');
const _ = require('underscore');
const fs = require('fs');

class SearchModule {
    
    constructor() {
        this.data = parse(
            fs.readFileSync(__dirname + '/sample_search.csv'), 
            {columns: true}
        );
        
        this.data = this.data.map(row => {
            row['con'] = row['pre'] + ' ' + row['post'] + ' ' + row['refs']
            return row;
        });

        let idx = -1;
        this.equations = _.map(this.data, row => {
            idx += 1;
            return {
                eqn: row['eqn'],
                idx: idx
            }
        });

        idx = -1;
        this.contexts = _.map(this.data, row => {
            idx += 1;
            return {
                con: row['pre'] + ' ' + row['post'] + ' ' + row['refs'],
                idx: idx
            }
        });
    }

    getByContextTerm (contextString, limit = 10) {
        let scores = 
            _.filter(this.data, row => {
                return (row['con'].indexOf(contextString) != -1);
            })
            .map(row => {
                row.score = row.con.split(contextString).length - 1;
                return row;
            });

        return scores;
    }

    getByEquationTerm (equationString, limit = 10) {
        let scores = 
        _.filter(this.data, row => {
            return (row['eqn'].indexOf(equationString) != -1);
        })
        .map(row => {
            row.score = row.eqn.split(equationString).length - 1;
            return row;
        });

        return scores;
    }

    search(contextString, equationString) {
        let conMatches = this.getByContextTerm(contextString);
        console.log(conMatches);
        let eqnMatches = this.getByEquationTerm(equationString);

        let combined = [];
        
        _.each(conMatches, match => combined.push(match));
        _.each(eqnMatches, match => combined.push(match));
        
        return combined;
    }
}

module.exports = SearchModule;