import { BASE_URL } from './api.js'

export async function signUp(email,password,userType,confirmPassword) {

    const response = await fetch(`${BASE_URL}/api/add_user`,{
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



export async function  login(email,password) {

    const response = await fetch(`${BASE_URL}/api/authenticate_user`,{
        method: 'POST',
        body: JSON.stringify({
            email:email,
            password:password

        })
    })

    const data = await response.json()
    return data.message

    
}