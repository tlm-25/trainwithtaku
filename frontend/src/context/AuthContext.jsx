import { useState, useEffect, useContext, createContext } from "react";
import {useNavigate} from "react-router-dom";
//initialise context - create context object - allow to share data globally across components without passing props manually
const AuthContext = createContext()



//create custom react hook from which we can destructure any of these values
//returns context's value - don't need to import useContext and AuthContext everywhere  
export function useAuth() {
    return useContext(AuthContext)
}


//wrapper component to place at top level of react app (in index.js or App.js) - holds state of logged in user
export function AuthProvider(props){
    //destructure children from the props - wrapper for everything in app, supplies auth state
    const {children} = props
    //state for user 
    const [globalUser, setGlobalUser] = useState(null);

    const [accessToken,setAccessToken] = useState(null)
    const [isLoading,setIsLoading] = useState(false);

    const navigate = useNavigate()

   
    
    
    
    
    
    
    
    
    
    
    async function signUp(email,password,userType,confirmPassword) {

        const response = await fetch(`/api/add_user`,{
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
            console.log(data)
            

                return {message: data.message,
                        status: response.status

                }


    
            
    }


    // authenticate a user trying to log in
    async function  login(email,password) {

        const response = await fetch("/api/login_with_access_token", {
        method: "POST",
        credentials: "include",
        headers: {
            //expected content type for the fastapi endpoint with Oauth form authentication - use URLSearchParams to format body content as form data
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: new URLSearchParams({
            
            username: email,   
            password: password
        })
    });

        if (response.ok) {

            //if user enters correct credentials, set the global user state using the access token to give the user access to resources
            const data = await response.json()
            setGlobalUser({ email:email})
            setAccessToken(data.access_token)
            return {
                status: response.status,
                message: data.message
            }

        }

        else {

            //if user enters incorrect credentials, simply return the message (which will indicate that they input invalid credentials)
            const data = await response.json()
            
            return {status: response.status,
                    message: data.message
                }


        }

        
        
    }


    // refresh access token using refresh token if user has valid refresh

    async function refreshAccessToken() {

        try{
            const response = await fetch("/api/refresh",{
                    method: "POST",
                    // tell browser to send crednetials to backend (e.g. cookies) 
                    credentials: "include",
                    headers: {
                        "Content-Type": "application/json"
                    }
                })

                if(!response.ok){
                    // if token is invalid or expired, log user out by clearing global user and access token
                    setGlobalUser(null)
                    setAccessToken(null)
                    console.log(response.json())
                }

                else {
                    const data = await response.json()
       
                    setAccessToken(data.access_token)
                    return data.access_token
                }

        }
    
        catch (error) {
            console.error("Failed to refresh access token",error)
            setGlobalUser(null)
            setAccessToken(null)
        }

 

    }




    async function logout(){

        try {

            const response = await fetch("/api/logout",{
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/json"
                }
            })

        } catch(error){
            console.error("Logout failed",error)
        }

        finally{
            setGlobalUser(null)
            setAccessToken(null)

            //navigate back to  landing page after user signs out
            navigate("/"); 


        }


        
    }

    // fetch with the access token (use for protected endpoints that require user to be logged in)
    async function fetchWithAuth(url,options={}){

        let token = accessToken

        //if access token expired, try to refresh it 
        if(!token){
            token = await refreshAccessToken()
        }
        //if no token avaliable, return null (user needs to log in)
        if (!token) return null 

        const buildOptions = (token) => ({
            //spread exisiting metadata (e.g. method, body,signal), add auth metadata
            ...options,
            credentials: "include",
            headers:{
                ...options.headers,
                //these headers will be included in every request
                "Authorization": `Bearer ${token}`,
                "Content-Type":"application/json"

            }
        })

        let response = await fetch(url,buildOptions(token))

        //if token invalid, try to refresh and retry request once
        if (response.status ===401){
            //if access token invalid, try to refresh and retry request once
            const newToken = await refreshAccessToken()
            if (!token) return null
            response = await fetch(url,buildOptions(newToken))

        }
        return response

    }




    //anything contained here becomes part of the gloabl state - accessible anywhere in application
    //anything in here is shared via context
    const value = {globalUser, isLoading, signUp,login,logout, fetchWithAuth}
    //takes two arguments - first is a callback function (function that runs when the event we are looking or is triggered)
    //second is a dependency array that contains (or doesn't contain) when this logic gets run
    //we leave dependency array empty, want this logic to run when the page loads for the first time
    useEffect(()=>{
        // check that user has a valid a
        async function checkAuth() {
            try {

                const token = await refreshAccessToken()
                
                // fetch the authenticated user's information from the backend using the access token (if it exists)
                
                if(token){
                    const response = await fetch("/api/me",{
                    method: "GET",
                    credentials: "include",
                    headers: {"Authorization": `Bearer ${token}`}
                })

                if(response.ok){
                    const data = await response.json()
                    console.log("authethenticated")
                    console.log(data)

                    //store the authenticated user in the global state - allow the rest of the app to know that the user has logged in 
                    setGlobalUser({ email: data.user_email })
                    setAccessToken(token)
                } else {
                    //if response gives an error- user is not authenticated, clear any exisiting user state
                    setGlobalUser(null)
                    setAccessToken(null)
                }

            
                    
                }


            }

            catch (error) {
                //if something fails (e.g. if the server is down, or there is a network error)
                //we assume that the user is not authenticated
                console.error("Auth check failed",error)
                setGlobalUser(null)
                setAccessToken(null)

            }

        }

        //invoke the authentication check 
        checkAuth()



    
    },[])


    return (

        //provde value to all components in provider - available to all children

        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>


    )






} 