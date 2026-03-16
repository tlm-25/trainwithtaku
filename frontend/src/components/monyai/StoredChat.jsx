
import {useState} from 'react'
import { useAuth } from '../../context/AuthContext';

function StoredChat(props){

    // Get chat id for specific user 

    const {conversationId,setChatLogFunction,setCurrentChatIDFunction,currentChatID,allStoredChatsState,setAllStoredChatsFunction,currentChatLogState, index, chatSelectedFlag, setChatSelectedFlagFunction, getSpecificChatFunction} = props

    const {globalUser} = useAuth()


    function replaceLastNCharacters(string,n){

        const choppedString = string.slice(0,-n)
        const replacementString = "x".repeat(n)

        const updatedString = choppedString + replacementString
        return updatedString




    }






    async function getSpecificChat (conversationId) {



            //get the specific chat from the chat history 
            const response = await fetch(`http://localhost:8000/get_chat_history`,{
            method: 'POST',
            headers:{
            "Content-Type": "application/json",
            "Authorization": `Bearer ${globalUser.token}`,
           },
            body: JSON.stringify({conversation_id:conversationId})

            })

            if (response.ok){
                const data = await response.json()
                console.log(data)



                setChatLogFunction(data)
                setChatSelectedFlagFunction(true)
                setCurrentChatIDFunction(conversationId)
                

            }

    };


    const deleteChat = async () => {

        const confirmed = window.confirm("Are you sure you want to delete this chat?");
        console.log(`${allStoredChatsState}`)

        //get the previous frontend token compared to the one that's been selected
        const originalChatArraySize = allStoredChatsState.length

        // const previousChatID = allStoredChatsState[allStoredChatsState.length-2].conversation_id

        // //frontend token of the next element in the array
        const currentChatIndex = allStoredChatsState.findIndex(chat => chat.conversation_id ===conversationId )

        
        



        // const firstChatID = allStoredChatsState[0].conversation_id


        //if user changes mind about deleting chat and clicks 'no' when they are asked to confirm
        if (!confirmed) return;

        //if no chat currently selected, just delete it and don't select a chat

        
        if (!chatSelectedFlag) {
            const response = await fetch(`http://localhost:8000/delete_chat`, {
            method: "DELETE",
            body: JSON.stringify({
                conversation_id: conversationId

            }),

            headers: {
                "Authorization": `Bearer ${globalUser.token}`,
                "Content-Type": "application/json"
            }

            });

            if (!response.ok) return;

            setAllStoredChatsFunction(prev =>
            prev.filter(chat => chat.conversation_id !== conversationId)
            );

            if (allStoredChatsState.length === 1) {
            setChatSelectedFlagFunction(false);
            setChatLogFunction([]);
            setCurrentChatIDFunction(null);
            }

            return;
        }

        // //update the allStoredChats array
        // setAllStoredChatsFunction(prev =>
        // prev.filter(chat => chat.conversation_id !== conversationId)
        // );


        

        //if there is a chat that is currently selected selected
        else if(chatSelectedFlag){
            //placeholder for target chat ID after a chat is deleted 
            let targetChatID = null;

            //if there is more than one chat remaining before we delete it
            if(originalChatArraySize > 1){

                //if there exists a chat after the chat we are currently on
                if(currentChatIndex + 1 < allStoredChatsState.length) {
                    targetChatID = allStoredChatsState[currentChatIndex + 1].conversation_id


                }

                //if there is no chat after the one we are currently on and there is a chat before it - select the chat before
                else if (currentChatIndex - 1 >= 0) {

                    targetChatID = allStoredChatsState[currentChatIndex - 1].conversation_id

                }


                const response = await fetch(`http://localhost:8000/delete_chat`, {
                    method: "DELETE",
                    body: JSON.stringify({
                    conversation_id: conversationId

                    }),

                    headers: {
                        "Authorization": `Bearer ${globalUser.token}`,
                        "Content-Type": "application/json"
                    }

                    });


                setAllStoredChatsFunction(prev =>
                 prev.filter(chat => chat.conversation_id !== conversationId)
                );

               

            }
            if(targetChatID){
                 await getSpecificChat(targetChatID)
            }
            
            //if we delete the last chat
            else {

                const response = await fetch(`http://localhost:8000/delete_chat`, {
                method: "DELETE",
                body: JSON.stringify({
                conversation_id: conversationId

                }),

                headers: {
                    "Authorization": `Bearer ${globalUser.token}`,
                    "Content-Type": "application/json"
                    }

                });


                setAllStoredChatsFunction(prev =>
                 prev.filter(chat => chat.conversation_id !== conversationId)
                );

                //set the chatSelected state false to indicate that no chat is selected
                setChatSelectedFlagFunction(false)
                //display an empty chat log
                setChatLogFunction([])
                //set the current chat id value null
                setCurrentChatIDFunction(null)

            }




        }

        

        
    };


    
    return (
        <>
            
            <button className={`chat-preview-block  ${currentChatID===conversationId ? "chat-selected":""}`} onClick={()=>{getSpecificChat(conversationId)}}>
                <p> Chat: {conversationId ? index:"New chat..."}</p>

                    <p onClick={deleteChat} className={`delete-chat-button`}><i className="fa-solid fa-trash-can"></i></p>

            </button>



            
        
        
        
        </>
    )

}






export default StoredChat;