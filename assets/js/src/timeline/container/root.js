import React, {Component} from 'react';
import axios from 'axios';
import styles from '../styles.css';
import Bg from '../components/bg'
import Card from '../components/card';
import {Aux} from '../../common';

class TimelineWidget extends Component{
    state = {
        data: [
            
        ]
    }

    componentDidMount(){
        axios({
            'method': 'GET',
            'url': this.props.dataURL
        }).then((res) =>{
            this.setState({data: this.props.resProcessor(res)})
        })
    }


    render(){
        return(
            <Aux>
                <h4 style={{fontWeight: 200}}>Timeline</h4>
                <div className={styles.timelineContainer}>
                    <Bg cards={this.state.data.length}/>
                    <div className={styles.transparentOverlay}>
                        {this.state.data.map((details, i) =>(
                            <Card {...details} index={i}/>
                        ))}
                    </div>
                </div>
            </Aux>
        )
    }
}

export default TimelineWidget