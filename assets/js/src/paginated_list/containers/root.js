import React, {Component} from 'react';
import axios from 'axios';

import Headings from '../components/headings';
import Row from '../components/rows';
/**
 * This widget takes a paginated serializer and lists the elements in the 
 * seriailizer as pages that can be cycled through
 * props 
 * dataURL - the url to fetch the data
 * resHandler - used to handle the fetched data
 * headings -an array of strings 
 * actionData - an array of objects containing url + name
 * rowFields - an array of strings for the fields to be displayed in arow
 */


 class PaginatedList extends Component{
     state = {
         currentPage: 1,
         hasNextPage: false,
         rows: []
     }

     componentDidMount(){
        axios({
            url: this.props.dataURL,
            method: 'get'
        }).then((res) => this.props.resHandler(this, res))
        //set has next page 
     }

     loadNextPage = () =>{
        if(this.state.hasNextPage){
            axios({
                url: this.props.dataURL,
                method: 'get',
                data: {
                    page: this.state.currentPage + 1
                }
            }).then((res) => this.props.resHandler(this, res))
        }
     }

     render(){
         return(
             <div>
                <table className="table">
                    <Headings headings={this.props.headings} />
                    <tbody>
                        {this.state.rows.map((rowData, i) =>(
                        <Row 
                            rowData={rowData}
                            rowFields={this.props.rowFields}
                            key={i}
                            actionData={this.props.actionData}/>
                        ))}                    
                    </tbody>
                    <tfoot>
                            <td colSpan={this.props.headings.length - 1}></td>
                            <td>
                                <button
                                    className="btn btn-primary"
                                    disabled={this.state.hasNextPage}
                                    onClick={this.loadNextPage}>Next</button>
                            </td>
                    </tfoot>
                </table>
             </div>
         )
     }
 }

 export default PaginatedList;