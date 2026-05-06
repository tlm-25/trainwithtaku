import { useState,useContext, createContext,useRef } from "react";

const ChatContext = createContext();

export function useChatStreamContext(){
    //global state to store current stream for key value pair 

    return useContext(ChatContext);

}


export function ChatProvider(props) {
    const {children} = props

    // ref to store chatbot response string while it is being streamed
    //storing ref so we can access the state without rerendering
    const bufferRef = useRef({});

    const [streamBuffer, setStreamBuffer] = useState({});


    // streaming ref 

    function appendStringToBuffer(conversationId,chunk){
        //if conversation id is not in ref, create new buffer with empty string for specific convo id
        if(!bufferRef.current[conversationId]){
            //create new buffer for this conversation id
            bufferRef.current[conversationId] = { text: "", sources: null, isDone: false };
            
        }
        // append chunk 
        bufferRef.current[conversationId].text+=chunk;

        /*update the state to trigger re-render and update the UI with new buffer content
        update the text display for specific conversation in UI
        */ 
        setStreamBuffer((prev)=>({
                ...prev,
                [conversationId]: {
                    ...bufferRef.current[conversationId]

            }
        }));




    }
    //finalise buffer when streaming done, set isDone to true and add sources if available
    function finalizeBuffer(conversationId, sources = null) {
        if (bufferRef.current[conversationId]) {
            bufferRef.current[conversationId].isDone = true;
            bufferRef.current[conversationId].sources = sources;
        }

        setStreamBuffer(prev => ({
            ...prev,
            [conversationId]: { ...bufferRef.current[conversationId] }
        }));
    }


    function removeBuffer(conversationId){

        // remove specific convo id from state and ref

        if(buffer[conversationId]){
            delete bufferRef.current[conversationId];
        }

        setStreamBuffer((prev)=>{
            // create new object without the conversation id key to trigger re-render and update UI
            const { [conversationId]: _, ...rest } = prev;
            return rest;



        })

    }


    
    //anything contained here becomes part of the gloabl state - accessible anywhere in application
    //anything in here is shared via context
    const value = {appendStringToBuffer,finalizeBuffer,bufferRef}






    return (
        <ChatContext.Provider value = {value}>
            {children}
        </ChatContext.Provider>
    )

    
}
