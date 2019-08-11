import React, {Component} from 'react';
import axios from 'axios';
import styles from '../styles.css';
import Bg from '../components/bg'
import Card from '../components/card';


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
            <div className={styles.timelineContainer}>
                <Bg />
                <div className={styles.transparentOverlay}>
                    {this.state.data.map((details, i) =>(
                        <Card {...details} index={i}/>
                    ))}
                </div>
            </div>
        )
    }
}

export default TimelineWidget