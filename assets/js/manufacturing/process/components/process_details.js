import React, {Component} from 'react';
import RateWidget from './rate_widget';
import TimeField from '../../../src/components/time_field';
import AsyncSelect from '../../../src/components/async_select';



class ProcessDetails extends Component{
    state = {
        process: null,
        processRate: {},
        type: 0,
        token: ""

    }

    componentDidMount(){
        const token =document.querySelector('input[name="csrfmiddlewaretoken"]');
        this.setState({token: token.value});
    }

    processHandler =(processID) =>{
        this.setState({process: processID});
    }

    inputHandler = (evt) =>{
        const name = evt.target.name;
        const value = evt.target.value;
        let newState = {...this.state};
        newState[name] = value;
        this.setState(newState);
    }

    clickHandler = (data) =>{
        this.setState({processRate: data});
    }

    durationHandler = (data, name) =>{
        if(!data.valid && data.value.length == 5){
            alert('Please provide a proper duration');
        }else if(data.valid){
            this.setState({duration: data.value})
        }else{
            return null;
        }
    }
    render(){
        return(
            <div>
                <form action="" method="POST">
                <input type="hidden" name="materials" id="id_materials" value=""/>
                <input type="hidden" name="equipment" id="id_equipment" value=""/>
                <input type="hidden" name="products" id="id_products" value=""/>
                <input type="hidden" name="csrfmiddlewaretoken" value={this.state.token}/>
                <p>Name</p>
                    <input 
                        type="text" 
                        className="form-control"
                        name="name"
                        onChange={this.inputHandler} />
                <p>Description</p>    
                    <textarea 
                        name="description"
                        className="form-control"
                        onChange={this.inputHandler}
                        cols={40}
                        rows={10}></textarea>
                <p>Type of Process(line, batch)</p>                   
                    <select
                        className="form-control"
                        onChange={this.inputHandler}
                        name="type">
                        <option value={0}>Line</option>
                        <option value={1}>Batch</option>
                    </select>
                <p>Process Rate/Duration</p>
                    {this.state.type === "0"
                    ? <RateWidget 
                        clickHandler={this.clickHandler}/>
                    : <TimeField 
                        initial="00:00"
                        name="duration"
                        handler={this.durationHandler}
                        />}
                <p>Parent Process</p>                
                    <AsyncSelect 
                        dataURL="/manufacturing/api/process/"
                        handler={this.processHandler}
                        resProcessor={(res) =>{
                            return res.data.map((p)=>({
                                value: p.id,
                                name: p.name
                            }))
                        }}/>
                <br />
                <button className="btn btn-success">Create!</button>
                </form>
            </div>
        )
    }
}

export default ProcessDetails;