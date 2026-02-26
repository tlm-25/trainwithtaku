import { useState, useEffect, useContext, createContext } from "react";
import { login, signUp } from "../userFunctions";
//initialise context - create context object - allow to share data globally across components without passing props manually
const authContext = createContext()

//create custom react hook from which we can destructure any of these values
//returns context's value - don't need to import useContext and AuthContext everywhere  
export function useAuth() {
    return useContext(authContext)
}


//wrapper component to place at top level of react app (in index.js or App.js) - holds state of logged in user
export function AuthProvider(props){
    //destructure chidren from the props - wrapper for everythin in app, supplies auth state
    const {children} = props
    //state for user 
    const [globalUser, setGlobalUser] = useState(null);

    //if user is not authenticated we do not have a global state
    const [globalData, setGlobalData] = useState(null);

    const [isLoading,setIsLoading] = useState(false);

   
    async function signUp(email,password,userType,confirmPassword) {

        const response = await fetch(`http://localhost:8000/add_user`,{
            method: 'POST',
            headers: {
                "Content-Type":"application/json"
            },
            body: JSON.stringify({
                
                email:email,
                password:password,
                user_type:userType,
                confirm_password:confirmPassword})

            })

            const data = await response.json()

            return data.message
    }


    // authenticate a user trying to log in
    async function  login(email,password) {

        const response = await fetch("http://localhost:8000/login_with_access_token", {
        method: "POST",
        headers: {
            //expected content type for the fastapi endpoint with Oauth form authentication - use URLSearchParams to format body content as form data
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
            
            username: email,   
            password: password
        })
    });

        const data = await response.json()


        setGlobalUser({ email:email, token: data.access_token })
        return true

        
    }


    async function logout(){
        setGlobalUser(null)
    }


    //anything contained here becomes part of the gloabl state - accessible anywhere in application
    //anything in here is shared vis context
    const value = {globalUser, globalData, setGlobalData, isLoading, signUp,login,logout}
    //takes two arguments - first is a callback function (function that runs when the event we are looking or is triggered)
    //second is a dependency array that contains (or doesn't contain) when this logic gets run
    //we leave dependency array empty, want this logic to run when the page loads for the first time
    useEffect(()=>{

        //check if user is logged in when the app loads - check if there is a token 
    
    },[])






} 