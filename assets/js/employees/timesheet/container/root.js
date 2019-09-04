import React, {Component} from 'react';
import $ from 'jquery';
import axios from 'axios';
import EntryLine from '../components/entry_line';
import DataEntryLine from '../components/data_entry_line';
import EditLine from '../components/edit_line';

export default class TimeSheet extends Component{
    state = {
        lines: []
    }

    componentDidMount(){
        $('<input>').attr({
            type: 'hidden',
            name: 'lines',
            id: "id_lines" ,
            value: ""
        }).appendTo('form');
        
        const urlSegments = window.location.href.split('/');
        const tail = urlSegments[urlSegments.length - 1];
        if(tail !== 'create'){
            axios({
                url: '/employees/api/timesheet/' + tail,
                method: 'GET',

            }).then(res =>{
                this.setState({lines: res.data.attendanceline_set.map((line) =>(
                    {
                        editing: false,
                        date: line.date,
                        timeIn: line.time_in,
                        timeOut: line.time_out,
                        breaksTaken: line.lunch_duration,
                        workingTime: line.working_hours
                    }
                ))})
            })
            $('#id_lines').val(encodeURIComponent(JSON.stringify(this.state.lines)));
        }
    }
    
    formUpdateMethod = () =>{
        $('#id_lines').val(
            encodeURIComponent(
                JSON.stringify(this.state.lines)))
    }

    lineHandler = (data) =>{
        const reg = /[012]\d:[0-5]\d/;
        if(!reg.test(data.timeIn) || !reg.test(data.timeOut) ||
                !reg.test(data.breaksTaken)){
            alert('Ensure all the times entered are formatted as "HH:MM"');
        }else{
            let newLines = [...this.state.lines];
            newLines.push(data);
            this.setState({lines: newLines}, this.formUpdateMethod);
        }
    }
    
    toggleEditing = (index) =>{
        let line = {...this.state.lines[index]};
        line.editing = true;
        let newLines = [...this.state.lines];
        newLines[index] = line;

        this.setState({lines: newLines});
    }

    editLine = (data, index) =>{
        const reg = /[012]\d:[0-5]\d/;
        if(data.date === 0 || data.timeIn === 0 || 
                data.timeOut === 0  || data.breaksTaken === 0){
            alert('Please fill in all data');
        
        }else if(!reg.test(data.timeIn) || !reg.test(data.timeOut) ||
                !reg.test(data.breaksTaken)){
            alert('Ensure all the times entered are formatted as "HH:MM"');
        }else{
            let line = {
                editing: false,
                date: data.date,
                timeIn: data.timeIn,
                timeOut: data.timeOut,
                breaksTaken: data.breaksTaken,
                workingTime: "00:00"
            };
            let newLines = [...this.state.lines];
            newLines[index] = line;
            this.setState({lines: newLines}, this.formUpdateMethod);
        }
    }

    deleteHandler = (index) =>{
        let newLines = [...this.state.lines];
        newLines.splice(index, 1);
        this.setState({lines: newLines}, this.formUpdateMethod);
    }
    render(){
        
        return(
            <table className="table table-sm">
                <thead>
                    <tr className="bg-primary">
                        <th>Date</th>
                        <th>Time In</th>
                        <th>Time Out</th>
                        <th>Breaks Taken</th>
                        <th>Total Working Hours</th> 
                        <th>Action</th>   
                    </tr>    
                </thead>
                <tbody>
                    {this.state.lines.map((line, i) =>{
                        if(line.editing){
                            return (<EditLine 
                                        editHandler={this.editLine}
                                        index={i}
                                        initData={line}
                                        key={i}/>)
                        }else{
                            return (<EntryLine 
                                key={i}
                                data={line}
                                index={i}
                                deleteHandler={this.deleteHandler}
                                editHandler={this.toggleEditing}
                            />)
                        }
                    }
                    )}
                    <DataEntryLine
                        insertLine={this.lineHandler}/>
            </tbody>
        
            </table>
        );
    }
}
