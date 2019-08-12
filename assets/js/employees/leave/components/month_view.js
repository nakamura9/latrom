import React, {Component} from 'react';
import axios from 'axios';
import Leave from './leave';
class MonthView extends Component{
    state = {
        title: "Month",
        leave: []
    }

    componentDidMount = () =>{
        this.props.linkUpdater();
        const params = this.props.match.params;

        axios.get(`/employees/api/month/${params.year}/${params.month}`)
            .then(res =>{
                this.setState({...res.data});
            })
    }
    
    render(){
        const days = [...Array(31).keys()];
        return(
            <div style={{
                border: "1 px solid #07f",
                height: "820px"
            }}>
                <div 
                    style={{
                        padding: "20px",
                        backgroundColor: "#07f",
                        color: "white",
                        width: "100%"
                    }}>
                    <h3>{this.state.title}</h3>
                </div>
                <div>
                    <table style={{
                        width: "95%",
                        position: "absolute",
                        top: "90px"
                    }}>
                        <tbody>
                            {days.map((day, i) =>(
                                <tr 
                                    height={20}
                                    key={i}
                                    style={{
                                        borderTop: "1px solid #ccc"
                                    }}>
                                    <td
                                        style={{width:"20%"}}>
                                        {i + 1}
                                    </td>
                                    <td style={{width:"80%"}}>
                                    &nbsp;</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                    {this.state.leave.map((leave, i) =>(
                        <Leave data={leave} offset={i * 151} key={i} />
                    ))}
                </div>
            </div>
        )
    }
}

export default MonthView;