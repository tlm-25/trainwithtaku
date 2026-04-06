import {useState, useEffect, useRef} from 'react'
import '../../index.css'
import StoredChat from './StoredChat';
import { getAllStoredChats } from '../../utils';
import { useAuth } from '../../context/AuthContext';
import {toast} from 'react-hot-toast'
import SourcesModal from './SourcesDisplayModal';
import ReactMarkdown from 'react-markdown'
function ChatWindow() {

    const [userInput, setUserInput] = useState('');
    const [chatLog, setChatLog] = useState([]);
    const [loading, setLoading] = useState(false);
    //boolean to check if a chat has been selected or not
    const [chatSelectedFlag,setChatSelectedFlag] = useState(false);
    //list of all chats created by the user
    const [allCreatedChats,setAllCreatedChats] = useState([]);

    //the conversation id of the current selected chat (not the conversation id of the backend)
    const [currentChatID,setCurrentChatID] = useState(null)
    //check if user is currently creating a chat or not
    const [creatingChat, setCreatingChat] = useState(false)

    const [showSourcesModal,setShowSourcesModal] = useState(false)

    const currentChatIDRef = useRef(null)

    //using useRef instead of useState to update value of streamed content without re-rendering
    const streamedTextRef = useRef("");

    const chatWindowBottomRef = useRef(null);





    //const queryID
    const [queryID, setQueryID] = useState(null)


    //controllerRef flag to indicate that
    const controllerRef = useRef(false)

    //tracking if user has pressed the cancel button
    const cancelledRef = useRef(null)

    const {globalUser,logout,fetchWithAuth} = useAuth()
    const [sidebarOpen, setSidebarOpen] = useState(false)

    const [messageSources,setMessageSources] = useState([])
    // Load chat history for current selected chat
    useEffect(() => {


    }, []);


    //Load previously created chats
    useEffect(()=>{




         getAllStoredChats(setAllCreatedChats,fetchWithAuth);
        

    },[])


    async function handleShowSources (sources) {

        // handle showing the references

        setShowSourcesModal(true); 
        setMessageSources(sources)


    }


    
    




    //every time a new message is in the chat, or a different chat is selected, scroll to the bottom of the chat area (everytime chatlog changes)
    useEffect(()=>{

        if(chatWindowBottomRef){
            chatWindowBottomRef.current.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' })

        }



    },[chatLog])

    //remove specific item from array
    function removeItem(array, valueToRemove) {
        return array.filter(
    	item => item !== valueToRemove);
    }




    //Load all stored chats into local storage


    const clearChatHistory = async (event) => {
        event.preventDefault();
        try{
            const response = await fetchWithAuth(`/api/clear_chat`, {
                method: 'POST',
                body: JSON.stringify({
                    conversation_id: currentChatID

                }),

            });

            if(response.ok){
                // console.log(currentChatID)
                // console.log(response)
                // setChatLog([{ type: 'bot', message: userInput,timestamp:String(now)])
                //get the specific chat from the chat history 
                const response = await fetchWithAuth(`/api/get_chat_history`,{
                method: 'POST',
                body: JSON.stringify({conversation_id:currentChatID}),


                })
                const chatData = await response.json()

                setChatLog([chatData[0]])
                await getAllStoredChats(setAllCreatedChats,fetchWithAuth)
                
            }
            

            


        }
        catch (error) {
            console.error("Failed to clear chat",error)
        }

    }

    async function createNewChat(event) {

        //if user not logged in, block creating a new chat
        if(!globalUser) {
            toast.error(` Please log in again to use the chatbot`,);
            return
            
        };

        event.preventDefault();
        setCreatingChat(true)

        //add the new chat to the database
        const response = await fetchWithAuth("/api/create_new_chat",{
            method: "POST"

        })

        //get the data about the chat and convert to json
        const data = await response.json()
        //get the updated list of chats
        await getAllStoredChats(setAllCreatedChats,fetchWithAuth)

        setCreatingChat(false)

        return data.conversation_id

        

    }





    //function to cancel generating an answer
    const handleCancelResponse= async (event) =>{
        event.preventDefault()

        //set the cancelled reference to true
        cancelledRef.current = true;
        //abort the original API request 
        controllerRef.current?.abort()
 
        //reset states
        setLoading(false)
        setUserInput("")
        streamedTextRef.current = ""
        setChatLog((prev) => {

            //creating shallow copy of chat log and removeing the last two elements (i.e. deleting the last user query and partially generated text from chatbot)
            const updatedChatlog = [...prev].slice(0,-2)

            // const latestUserQuery = updatedChatlog[updatedChatlog.length - 2]

            // //get the latest entry of the chat log (will have the blank text)
            // const latestMessage = updatedChatlog[updatedChatlog.length - 1]
            return updatedChatlog


        }); 

        //get cancel endpoint (with specific query id)
        const cancelEndpoint = `/api/cancel_response/${queryID}`
        fetch(cancelEndpoint,{
            method: "POST"
        }).then(res=>res.json()).then(console.log("cancelled")).catch(err => console.error("Failed to cancel", err));

        //delete that last message generated by the bot and the last query sent by the user from the chat log




        }
    

    async function streamChatbotAnswer(conversationId){

                //get the timestamp for when the message was sent
        const now = new Date().toISOString()
        // Don't allow user to send an empty message
        if (!userInput.trim()) return; 

        const userMessage = { type: 'user', message: userInput,timestamp:String(now) };
        console.log(now)
        
        // update chat log array 
        const newChatLog = [...chatLog, userMessage];
        setChatLog(newChatLog);
        setUserInput('');
        setLoading(true);

        //reset ref

        streamedTextRef.current = ""

            //browser api class which is used to cancel api requests 
            const controller = new AbortController()
            //saving this specific instance of abort controller - can call without rerender - access DOM directly
            //setting the global controller ref to this instance of the abort controller
            controllerRef.current = controller

            //returns an abort signal object instance to communicate with or abort an async operation - in this app, using it for 'cancelling'
            const signal = controllerRef.current.signal;
            cancelledRef.current = false;
    

        try {
            // The API call to our FastAPI backend
            const response = await fetchWithAuth("/api/chat", {
                method: "POST",

                body: JSON.stringify({
                    user_message: userMessage,
                    chat_history: newChatLog,
                    //may update to include client form later
                    client_form: null,
                    conversation_id: conversationId
                }),

                signal: signal
                
            });

            //get the the query ID of the user input
             const chatInputQueryID = response.headers.get("X-Query-ID")


             setQueryID(chatInputQueryID)

            


            if (response.ok){

                //read input data as a stream
                const reader = response.body.getReader()


                //create text decoder to decode binary data into text
                const decoder = new TextDecoder("utf-8")

                //checking to see if streaming done
                let done = false;

                const now =  new Date().toISOString()

                // Add an empty bot message to the chat log before the text streaming starts
                setChatLog(prev => [...prev, { type: 'bot', message: '', timestamp: String(now) }]);

                //while reading from streaming response
                while(!done){

                    //read a chunk of data from the stream
                    const {value, done: readerDone} = await reader.read()

                    //check if we've already read the last chunk in the stream
                    done = readerDone
                    if(done) {

                        break
                    };

                    if(value){
                        //DEcode the chunk
                        const chunkValue = decoder.decode(value,{stream: true})

                        
                        /*update the streamed text reference - only if the chunk value does not include the __REFS__ flag (which indicates that the chunk is the retrieved documents reference text, not part of the chatbot answer)
                        Everything after the __REFS__ is refernce text, and exists in a seperate chunk from the chatbot answer
                        
                        
                        */
                        if(!chunkValue.includes("__REFS__")){
                        streamedTextRef.current += chunkValue
                        //update chatlog with new streamed text - update the last message
                        //update the chatlog
                        setChatLog((prev)=>{
                            
                            //creating shallow copy of chat log - avoid mutating state directly for non-primitive typ
                            const updatedChatlog = [...prev]

                            //get the latest entry of the chat log (will have the blank text)
                            const latestMessage = updatedChatlog[updatedChatlog.length - 1]

                            //update the last entry with the streamed text
                            if(latestMessage.type === 'bot'){

                                //filling in  the empty string with the text retrieved from the front end
                                updatedChatlog[updatedChatlog.length - 1] = {
                                    ...latestMessage,
                                    message: streamedTextRef.current
                                }

                            }

                            
                            

                            return updatedChatlog

                            
                            });

                        }

                        else {
                            //Once the chatbot has finished streaming its answer

                            //if chunk includes "__REFS__" string, this means the chunk is the retrieved documenets reference and not part of the chatbot answer
                            const stringFormattedDocuments = chunkValue.split("__REFS__")[1]
                            // console.log(stringFormattedDocuments)

                            setChatLog((prev)=>{
                                const updatedChatlog = [...prev]
                                const latestMessage = updatedChatlog[updatedChatlog.length - 1]
                                if(latestMessage.type === 'bot'){
                                    updatedChatlog[updatedChatlog.length - 1] = {
                                        ...latestMessage,
                                        sources: stringFormattedDocuments
                                    }
                                }
                                return updatedChatlog
                            })

                        }
                        

                    }


                }


                // Ensure final version of chat is saved after stream finishes - save to local storage for persistence
                setChatLog(prev => {
                const finalChat = [...prev];
                // sessionstorage.setItem('chatLog', JSON.stringify(finalChat));
                return finalChat;
      });
                

            }

            else if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

        } catch (error) {
            console.error('Error fetching chat response:', error);

            //ignore abort errors as this is when the user cancels
            if(!error.name === "AbortError"){
                const now =  new Date().toISOString()
                //if connection fails for any other reason, show in the chat that 'Something went wrong' 
                const errorMessage = { type: 'error', message: 'Sorry, something went wrong. Please try again.',timestamp: String(now) };
                setChatLog(prev => [...prev, errorMessage]);

            }
            
        } finally {
            setLoading(false);
        }


    }
    

    

        



    const handleSubmit = async (event) => {
        event.preventDefault();
        
        // //if chat not yet selected (i.e.e user just starts typing)
        if(!chatSelectedFlag){
            //create a new chat id 
            const newChatID = await createNewChat(event)


            //get the specific chat based on chat ID
            const response = await fetchWithAuth(`/api/get_chat_history`,{
            method: 'POST',
            body: JSON.stringify({conversation_id:newChatID}),

            })

            if (response.ok){
                const data = await response.json()
                setChatLog(data)
                setCurrentChatID(newChatID)
                console.log("generating chat")
                console.log(newChatID)
                // send message to newly create chat, stream answer from chatbot
                await streamChatbotAnswer(newChatID)
                

            }
            
            
            setChatSelectedFlag(true)

            }
        else {

            // send message to selected chat, and stream the answer from the chatbot
            await streamChatbotAnswer(currentChatID)

        }

        

    

    };






    return (

            <div className='main-chatbot-container'>
                <SourcesModal showSourcesModal={showSourcesModal} setShowSourcesModalFunction={setShowSourcesModal} sourcesForCurrentMessage={messageSources}/>
                <button className="hamburger-button" onClick={() => setSidebarOpen(!sidebarOpen)}>
                    {sidebarOpen ? '✕' : '☰'}
                </button>

                <div className={`chat-selection-container${sidebarOpen ? ' sidebar-open' : ''}`}>
                    <img  src='/twt-logo.png' className='twt-logo'/>
                    <button disabled={creatingChat} onClick={(event)=>createNewChat(event)}>
                        + New Chat
                    </button>
                    {creatingChat &&<div className='creating-chat-message'>Creating new chat... </div>}
                    <div className='all-chats-container'>
                        
                        {allCreatedChats.map((storedChat,index)=>(

                                <StoredChat key={String(index)+storedChat.conversation_id} index = {index+1} conversationId = {storedChat.conversation_id} setChatLogFunction={setChatLog} setCurrentChatIDFunction={setCurrentChatID} currentChatID={currentChatID} setAllStoredChatsFunction={setAllCreatedChats} currentChatLogState={chatLog} chatSelectedFlag={chatSelectedFlag} setChatSelectedFlagFunction={setChatSelectedFlag} allStoredChatsState={allCreatedChats}/>
                            ))}

                    </div>
                </div>

                
                <div className='chat-area'>
                        
                    <div className="chat-window">
                        {chatLog.map((message, index) => (
                            <div key={`${message.timestamp}-${index}`}>
                                <div className={`message ${message.type}`}>
                                    <ReactMarkdown>{message.message}</ReactMarkdown>
                                </div>

                                {<p className='message-timestamp'>{String(message.timestamp).substring(8,10)+ "/"+ String(message.timestamp).substring(5,7)+"/"+String(message.timestamp).substring(0,4)+" "+String(message.timestamp).substring(11,16)}</p> } 
                                {/** If the message is from the chatbot (excluding initial greeting)*/}
                                {(message.type == 'bot' && message.message !=="" && !loading && index > 0)&&(
                                    <button className='show-sources-button' onClick={()=>{handleShowSources(message.sources)}}>View Sources</button>


                                )}
        
                            </div>
                        
                        ))}

                        <div ref={chatWindowBottomRef}></div>
                        
                    </div>

                    {!loading && <button className="cancel-query-button" onClick={clearChatHistory}>Clear chat history</button>}
                    { loading && <button className="cancel-query-button" onClick={handleCancelResponse} type="submit" >Cancel</button>}
                    <form onSubmit={handleSubmit} className="chat-form">

                        <input
                            type="text"
                            value={userInput}
                            onChange={(e) => setUserInput(e.target.value)}
                            placeholder="Enter your question"
                            disabled={loading ||creatingChat}
                        />
                        <button className="send-query-button" type="submit" disabled={creatingChat||loading||userInput==""}><i className="fa-solid fa-paper-plane"></i></button>
                    </form>
                    

                </div>

            </div>

        
        
        
    )

}



export default ChatWindow;