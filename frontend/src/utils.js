import { useAuth } from "./context/AuthContext";

export async function getAllStoredChats(setAllCreatedChatsFunction,token){




  try {
    const response = await fetch("http://127.0.0.1:8000/get_stored_user_chats", {
      method: "POST",
                  headers:{
                "Authorization": `Bearer ${token}`,
                "Content-Type":"application/json"
            }
    });

    if (!response.ok) throw new Error("Failed to fetch chats");

    const data = await response.json();
    setAllCreatedChatsFunction([...data]);
    return data; 
  } catch (err) {
    console.error("Error fetching chats:", err);
  }

  }

 

    


export  function removeValueFromArray(array,valueToRemove){

    return array.filter(item=>item!==valueToRemove)

}


