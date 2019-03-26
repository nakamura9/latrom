import React, {Component} from 'react';
import SearchableWidget from '../../src/components/searchable_widget';
import axios from 'axios';

class ServiceEntry extends Component{
    state = {
        hours: 0,
        rate: 0,
        fee: 0,
        selected: ''
    }
    componentDidUpdate(prevProps, prevState){
        if (this.props.itemList.length !== prevProps.itemList.length){
            this.setState({
                hours: 0,
                rate: 0,
                fee: 0
            })
            //remove selected choice from list of choices 
        }
    }

    handler = (evt) =>{
        const name = evt.target.name;
        let newState = {...this.state};
        newState[name] = evt.target.value;
        this.setState(newState);
        this.props.onChangeHours(evt);
    }

    selectHandler = (value) =>{
        const pk = value.split('-')[0];

        axios({
            method: 'get',
            url: '/services/api/service/' + pk
        }).then(res =>{
            this.setState({
                selected: value,
                rate: res.data.hourly_rate,
                fee: res.data.flat_fee
            }, () => this.props.onSelect(this.state))
        })
        
    }

    clearHandler = () =>{
        this.setState({
            rate: 0,
            hours: 0,
            fee: 0,
            selected: ""
        });
        this.props.onClear()
    }

    

    render(){
    
        const headStyle = {
            padding: '10px',
            backgroundColor: '#0099ff'
        }
        return(
            <div>
                <table style={{width:"100%"}}>
                    <thead>
                        <tr>
                            <th style={{...headStyle, width:'50%'}}>Service</th>
                            <th style={headStyle}>Flat Fee</th>
                            <th style={headStyle}>Hourly Rate</th>
                            <th style={headStyle}>Hours</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td >
                                <SearchableWidget
                                    list={this.props.itemList}
                                    dataURL="/services/api/service/"
                                    displayField="name"
                                    idField="id"
                                    canCreateNewItem={true}
                                    newLink='/services/create-service'
                                    onSelect={this.selectHandler}
                                    onClear={this.clearHandler} />
                            </td>
                            <td>
                                <input 
                                    type="number"
                                    className="form-control"
                                    name="fee"
                                    value={this.state.fee}
                                    onChange={this.handler}/>
                            </td>
                            <td>
                                <input 
                                    type="number"
                                    className="form-control"
                                    name="rate"
                                    value={this.state.rate}
                                    onChange={this.handler}/>
                            </td>
                            <td>
                                <input 
                                    type="number"
                                    className="form-control"
                                    name="hours"
                                    value={this.state.hours}
                                    onChange={this.handler}/>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
        )
    };
}

export default ServiceEntry;