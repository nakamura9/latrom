import React, {Component} from 'react';
import axios from 'axios';
import Leave from './leave';

const Month = (props) => {
    const days = [...Array(31).keys()];

    return(
        <div>
            <div style={{
                minHeight: "820px",
                position: "relative"
            }}>
                <table style={{
                    width: "200px",
                    position: "absolute",
                    top: "40px"
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
                {props.data.map((leave, i) =>(
                    <Leave 
                        data={leave} 
                        key={i}
                        offset={-20} />
                ))}
            </div>
            
        </div>
    );
}

class YearView extends Component{
    state = {
        leave: [],
        year: 2018
    }
    componentDidMount = () => {
        this.props.linkUpdater();
        const params = this.props.match.params;
        
        axios.get(`/employees/api/year/${params.year}`)
        .then(res =>{
            this.setState({...res.data, year: params.year});
        })
    }
    
    render(){
        return(
            <div style={{
                width: "100%",
                overflowX: 'auto',
                maxHeight: 'inherit'
            }}>
                <table>
                    <tr>
                        {['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'].map((month, i) =>(
                            <th style={{
                                minWidth: "200px",
                                padding: "10px",
                                color: "white",
                                backgroundColor: "#07f"
                            }}>
                                <a 
                                    style={{
                                        color: "white"
                                    }}
                                    href={`/employees/leave-calendar/month/${this.state.year}/${i + 1}`}>
                                    {month}
                                </a></th>
                        ))}
                    </tr>
                    <tr>
                    {this.state.leave.map((month, i) =>(
                        <td>
                            <Month data={month}/>
                        </td>
                        ))}
                    </tr>
                </table>
            </div>
        );
    }
}

export default YearView;