import React, {Component} from 'react';
import styles from '../steps.css';
import Step from '../components/step';
import StepsBg from '../components/bg';

class StepsWidget extends Component{
    state = {
        steps: [{
            'name': 'quotation',
            'checked': 1
        },
        {
            'name': 'invoice',
            'checked': 0
        }
    ]
    }
    render(){
        return(
        <div className={styles.stepsContainer + " shadow"}>
            <StepsBg />
            {this.state.steps.map((step) =>{
                return(<Step {...step} />)
            })}
        </div>

        )
    }
}

export default StepsWidget;