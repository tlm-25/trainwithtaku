import { useState } from "react";
import Modal from "../Modal";
//SourcesModal - a pop up that shows the sources used to help the chatbot generate it's answer
import SourcesDisplayContent from "./SourcesDisplayContent";
function SourcesModal(props){

    const {showSourcesModal, setShowSourcesModalFunction, sourcesForCurrentMessage} = props
            function handleCloseModal(){
            setShowModal(false)
        }
    


    return (

        <>
        <Modal showModal={showSourcesModal}  handleCloseModal={()=>setShowSourcesModalFunction(false)}>

            <SourcesDisplayContent sourcesForCurrentMessage={sourcesForCurrentMessage}/>     
        </Modal>
        
        </>
    )



}


export default SourcesModal;