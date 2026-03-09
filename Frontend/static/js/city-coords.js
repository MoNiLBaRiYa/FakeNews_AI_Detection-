/**
 * City Coordinates Database for ThruthGuard AI Threat Map
 * Covers Indian cities with focus on Gujarat, especially small towns & talukas.
 * Format: { lat, lon, label, state }
 */
var CITY_COORDS = {
    // ─── GUJARAT – Major Cities ───────────────────────────────────────────────
    'ahmedabad': { lat: 23.0225, lon: 72.5714, label: 'Ahmedabad', state: 'Gujarat' },
    'amdavad': { lat: 23.0225, lon: 72.5714, label: 'Ahmedabad', state: 'Gujarat' },
    'surat': { lat: 21.1702, lon: 72.8311, label: 'Surat', state: 'Gujarat' },
    'vadodara': { lat: 22.3072, lon: 73.1812, label: 'Vadodara', state: 'Gujarat' },
    'baroda': { lat: 22.3072, lon: 73.1812, label: 'Vadodara', state: 'Gujarat' },
    'rajkot': { lat: 22.3039, lon: 70.8022, label: 'Rajkot', state: 'Gujarat' },

    // ─── GUJARAT – Saurashtra / Gir Somnath District ─────────────────────────
    'talala': { lat: 20.9318, lon: 70.4614, label: 'Talala', state: 'Gujarat' },
    'talala gir': { lat: 20.9318, lon: 70.4614, label: 'Talala', state: 'Gujarat' },
    'somnath': { lat: 20.8880, lon: 70.4013, label: 'Somnath', state: 'Gujarat' },
    'veraval': { lat: 20.9001, lon: 70.3628, label: 'Veraval', state: 'Gujarat' },
    'gir somnath': { lat: 20.9000, lon: 70.3500, label: 'Gir Somnath', state: 'Gujarat' },
    'una': { lat: 20.8228, lon: 71.0391, label: 'Una', state: 'Gujarat' },
    'kodinar': { lat: 20.7893, lon: 70.7073, label: 'Kodinar', state: 'Gujarat' },
    'sutrapada': { lat: 20.8561, lon: 70.5208, label: 'Sutrapada', state: 'Gujarat' },

    // ─── GUJARAT – Junagadh District ─────────────────────────────────────────
    'junagadh': { lat: 21.5222, lon: 70.4579, label: 'Junagadh', state: 'Gujarat' },
    'keshod': { lat: 21.2985, lon: 70.2479, label: 'Keshod', state: 'Gujarat' },
    'visavadar': { lat: 21.3388, lon: 70.7363, label: 'Visavadar', state: 'Gujarat' },
    'manavadar': { lat: 21.4993, lon: 70.1409, label: 'Manavadar', state: 'Gujarat' },
    'vanthali': { lat: 21.4744, lon: 70.3258, label: 'Vanthali', state: 'Gujarat' },

    // ─── GUJARAT – Porbandar District ────────────────────────────────────────
    'porbandar': { lat: 21.6428, lon: 69.6100, label: 'Porbandar', state: 'Gujarat' },
    'ranavav': { lat: 21.7189, lon: 69.7458, label: 'Ranavav', state: 'Gujarat' },
    'kutiyana': { lat: 21.6227, lon: 69.9806, label: 'Kutiyana', state: 'Gujarat' },

    // ─── GUJARAT – Jamnagar District ─────────────────────────────────────────
    'jamnagar': { lat: 22.4707, lon: 70.0577, label: 'Jamnagar', state: 'Gujarat' },
    'dwarka': { lat: 22.2394, lon: 68.9678, label: 'Dwarka', state: 'Gujarat' },
    'okha': { lat: 22.4642, lon: 69.0731, label: 'Okha', state: 'Gujarat' },
    'khambhalia': { lat: 22.2011, lon: 69.6523, label: 'Khambhalia', state: 'Gujarat' },
    'lalpur': { lat: 22.3659, lon: 70.2658, label: 'Lalpur', state: 'Gujarat' },

    // ─── GUJARAT – Amreli District ────────────────────────────────────────────
    'amreli': { lat: 21.6021, lon: 71.2200, label: 'Amreli', state: 'Gujarat' },
    'rajula': { lat: 21.0370, lon: 71.4396, label: 'Rajula', state: 'Gujarat' },
    'lathi': { lat: 21.7278, lon: 71.3912, label: 'Lathi', state: 'Gujarat' },
    'dhari': { lat: 21.3260, lon: 71.0204, label: 'Dhari', state: 'Gujarat' },
    'bagasara': { lat: 21.4857, lon: 71.0111, label: 'Bagasara', state: 'Gujarat' },
    'savarkundla': { lat: 21.3419, lon: 71.3122, label: 'Savarkundla', state: 'Gujarat' },
    'khambha': { lat: 21.2180, lon: 71.5649, label: 'Khambha', state: 'Gujarat' },

    // ─── GUJARAT – Bhavnagar District ────────────────────────────────────────
    'bhavnagar': { lat: 21.7645, lon: 72.1519, label: 'Bhavnagar', state: 'Gujarat' },
    'sihor': { lat: 21.7178, lon: 71.9636, label: 'Sihor', state: 'Gujarat' },
    'palitana': { lat: 21.5247, lon: 71.8233, label: 'Palitana', state: 'Gujarat' },
    'mahuva': { lat: 21.0908, lon: 71.7558, label: 'Mahuva', state: 'Gujarat' },
    'ghogha': { lat: 21.6897, lon: 72.2736, label: 'Ghogha', state: 'Gujarat' },

    // ─── GUJARAT – Surendranagar District ────────────────────────────────────
    'surendranagar': { lat: 22.7272, lon: 71.6492, label: 'Surendranagar', state: 'Gujarat' },
    'wadhwan': { lat: 22.7147, lon: 71.6747, label: 'Wadhwan', state: 'Gujarat' },
    'dhrangadhra': { lat: 22.9943, lon: 71.4675, label: 'Dhrangadhra', state: 'Gujarat' },
    'halvad': { lat: 23.0190, lon: 71.1830, label: 'Halvad', state: 'Gujarat' },
    'limbdi': { lat: 22.5656, lon: 71.8232, label: 'Limbdi', state: 'Gujarat' },

    // ─── GUJARAT – Morbi District ─────────────────────────────────────────────
    'morbi': { lat: 22.8153, lon: 70.8380, label: 'Morbi', state: 'Gujarat' },
    'wankaner': { lat: 22.6120, lon: 70.9494, label: 'Wankaner', state: 'Gujarat' },
    'maliya': { lat: 22.8337, lon: 70.6088, label: 'Maliya', state: 'Gujarat' },

    // ─── GUJARAT – Kachchh District ───────────────────────────────────────────
    'bhuj': { lat: 23.2419, lon: 69.6669, label: 'Bhuj', state: 'Gujarat' },
    'gandhidham': { lat: 23.0754, lon: 70.1337, label: 'Gandhidham', state: 'Gujarat' },
    'anjar': { lat: 23.1092, lon: 70.0261, label: 'Anjar', state: 'Gujarat' },
    'mandvi': { lat: 22.8320, lon: 69.3566, label: 'Mandvi', state: 'Gujarat' },
    'kutch': { lat: 23.7337, lon: 69.8597, label: 'Kutch', state: 'Gujarat' },
    'kachchh': { lat: 23.7337, lon: 69.8597, label: 'Kachchh', state: 'Gujarat' },
    'mundra': { lat: 22.8427, lon: 69.7243, label: 'Mundra', state: 'Gujarat' },

    // ─── GUJARAT – Gandhinagar District ──────────────────────────────────────
    'gandhinagar': { lat: 23.2156, lon: 72.6369, label: 'Gandhinagar', state: 'Gujarat' },
    'mansa': { lat: 23.4270, lon: 72.6681, label: 'Mansa', state: 'Gujarat' },

    // ─── GUJARAT – Mehsana, Patan, Banaskantha ────────────────────────────────
    'mehsana': { lat: 23.5999, lon: 72.3693, label: 'Mehsana', state: 'Gujarat' },
    'patan': { lat: 23.8493, lon: 72.1266, label: 'Patan', state: 'Gujarat' },
    'palanpur': { lat: 24.1721, lon: 72.4382, label: 'Palanpur', state: 'Gujarat' },
    'deesa': { lat: 24.2579, lon: 72.1932, label: 'Deesa', state: 'Gujarat' },
    'unjha': { lat: 23.8050, lon: 72.3913, label: 'Unjha', state: 'Gujarat' },
    'visnagar': { lat: 23.6984, lon: 72.5497, label: 'Visnagar', state: 'Gujarat' },

    // ─── GUJARAT – Sabarkantha, Aravalli ─────────────────────────────────────
    'himmatnagar': { lat: 23.5981, lon: 72.9597, label: 'Himmatnagar', state: 'Gujarat' },
    'modasa': { lat: 23.4640, lon: 73.2950, label: 'Modasa', state: 'Gujarat' },
    'idar': { lat: 23.8307, lon: 73.0000, label: 'Idar', state: 'Gujarat' },

    // ─── GUJARAT – Anand, Kheda, Nadiad ──────────────────────────────────────
    'anand': { lat: 22.5645, lon: 72.9289, label: 'Anand', state: 'Gujarat' },
    'nadiad': { lat: 22.6916, lon: 72.8634, label: 'Nadiad', state: 'Gujarat' },
    'kheda': { lat: 22.7496, lon: 72.6873, label: 'Kheda', state: 'Gujarat' },
    'vallabh vidyanagar': { lat: 22.5410, lon: 72.9211, label: 'Vallabh Vidyanagar', state: 'Gujarat' },
    'petlad': { lat: 22.4770, lon: 72.8021, label: 'Petlad', state: 'Gujarat' },

    // ─── GUJARAT – Bharuch, Narmada ───────────────────────────────────────────
    'bharuch': { lat: 21.7051, lon: 72.9959, label: 'Bharuch', state: 'Gujarat' },
    'ankleshwar': { lat: 21.6264, lon: 73.0050, label: 'Ankleshwar', state: 'Gujarat' },
    'rajpipla': { lat: 21.8700, lon: 73.4986, label: 'Rajpipla', state: 'Gujarat' },

    // ─── GUJARAT – Navsari, Valsad, Dang ─────────────────────────────────────
    'navsari': { lat: 20.9466, lon: 72.9520, label: 'Navsari', state: 'Gujarat' },
    'valsad': { lat: 20.5992, lon: 72.9342, label: 'Valsad', state: 'Gujarat' },
    'vapi': { lat: 20.3714, lon: 72.9080, label: 'Vapi', state: 'Gujarat' },
    'bilimora': { lat: 20.7689, lon: 72.9600, label: 'Bilimora', state: 'Gujarat' },

    // ─── GUJARAT – Dahod, Panchmahal ─────────────────────────────────────────
    'godhra': { lat: 22.7773, lon: 73.6127, label: 'Godhra', state: 'Gujarat' },
    'dahod': { lat: 22.8368, lon: 74.2548, label: 'Dahod', state: 'Gujarat' },
    'halol': { lat: 22.5033, lon: 73.4716, label: 'Halol', state: 'Gujarat' },
    'kalol': { lat: 23.2499, lon: 73.4612, label: 'Kalol', state: 'Gujarat' },

    // ─── GUJARAT – Tapi, Surat Region ────────────────────────────────────────
    'vyara': { lat: 21.1115, lon: 73.3916, label: 'Vyara', state: 'Gujarat' },
    'bardoli': { lat: 21.1211, lon: 73.1134, label: 'Bardoli', state: 'Gujarat' },
    'olpad': { lat: 21.3302, lon: 72.7516, label: 'Olpad', state: 'Gujarat' },

    // ─── MAHARASHTRA ─────────────────────────────────────────────────────────
    'mumbai': { lat: 19.0760, lon: 72.8777, label: 'Mumbai', state: 'Maharashtra' },
    'pune': { lat: 18.5204, lon: 73.8567, label: 'Pune', state: 'Maharashtra' },
    'nagpur': { lat: 21.1458, lon: 79.0882, label: 'Nagpur', state: 'Maharashtra' },
    'nashik': { lat: 19.9975, lon: 73.7898, label: 'Nashik', state: 'Maharashtra' },
    'aurangabad': { lat: 19.8762, lon: 75.3433, label: 'Aurangabad', state: 'Maharashtra' },
    'thane': { lat: 19.2183, lon: 72.9781, label: 'Thane', state: 'Maharashtra' },
    'kolhapur': { lat: 16.7050, lon: 74.2433, label: 'Kolhapur', state: 'Maharashtra' },
    'navi mumbai': { lat: 19.0368, lon: 73.0158, label: 'Navi Mumbai', state: 'Maharashtra' },

    // ─── DELHI / NCR ─────────────────────────────────────────────────────────
    'delhi': { lat: 28.6139, lon: 77.2090, label: 'Delhi', state: 'Delhi' },
    'new delhi': { lat: 28.6139, lon: 77.2090, label: 'New Delhi', state: 'Delhi' },
    'noida': { lat: 28.5355, lon: 77.3910, label: 'Noida', state: 'Uttar Pradesh' },
    'gurgaon': { lat: 28.4595, lon: 77.0266, label: 'Gurgaon', state: 'Haryana' },
    'gurugram': { lat: 28.4595, lon: 77.0266, label: 'Gurugram', state: 'Haryana' },
    'faridabad': { lat: 28.4089, lon: 77.3178, label: 'Faridabad', state: 'Haryana' },

    // ─── KARNATAKA ───────────────────────────────────────────────────────────
    'bengaluru': { lat: 12.9716, lon: 77.5946, label: 'Bengaluru', state: 'Karnataka' },
    'bangalore': { lat: 12.9716, lon: 77.5946, label: 'Bengaluru', state: 'Karnataka' },
    'mysuru': { lat: 12.2958, lon: 76.6394, label: 'Mysuru', state: 'Karnataka' },
    'mysore': { lat: 12.2958, lon: 76.6394, label: 'Mysuru', state: 'Karnataka' },
    'hubli': { lat: 15.3647, lon: 75.1240, label: 'Hubli', state: 'Karnataka' },
    'mangaluru': { lat: 12.9141, lon: 74.8560, label: 'Mangaluru', state: 'Karnataka' },

    // ─── TAMIL NADU ──────────────────────────────────────────────────────────
    'chennai': { lat: 13.0827, lon: 80.2707, label: 'Chennai', state: 'Tamil Nadu' },
    'coimbatore': { lat: 11.0168, lon: 76.9558, label: 'Coimbatore', state: 'Tamil Nadu' },
    'madurai': { lat: 9.9252, lon: 78.1198, label: 'Madurai', state: 'Tamil Nadu' },

    // ─── TELANGANA ───────────────────────────────────────────────────────────
    'hyderabad': { lat: 17.3850, lon: 78.4867, label: 'Hyderabad', state: 'Telangana' },
    'secunderabad': { lat: 17.4399, lon: 78.4983, label: 'Secunderabad', state: 'Telangana' },
    'warangal': { lat: 17.9784, lon: 79.5941, label: 'Warangal', state: 'Telangana' },

    // ─── ANDHRA PRADESH ──────────────────────────────────────────────────────
    'visakhapatnam': { lat: 17.6868, lon: 83.2185, label: 'Visakhapatnam', state: 'Andhra Pradesh' },
    'vijayawada': { lat: 16.5062, lon: 80.6480, label: 'Vijayawada', state: 'Andhra Pradesh' },
    'tirupati': { lat: 13.6288, lon: 79.4192, label: 'Tirupati', state: 'Andhra Pradesh' },

    // ─── KERALA ──────────────────────────────────────────────────────────────
    'kochi': { lat: 9.9312, lon: 76.2673, label: 'Kochi', state: 'Kerala' },
    'thiruvananthapuram': { lat: 8.5241, lon: 76.9366, label: 'Thiruvananthapuram', state: 'Kerala' },
    'kozhikode': { lat: 11.2588, lon: 75.7804, label: 'Kozhikode', state: 'Kerala' },
    'thrissur': { lat: 10.5276, lon: 76.2144, label: 'Thrissur', state: 'Kerala' },

    // ─── RAJASTHAN ───────────────────────────────────────────────────────────
    'jaipur': { lat: 26.9124, lon: 75.7873, label: 'Jaipur', state: 'Rajasthan' },
    'jodhpur': { lat: 26.2389, lon: 73.0243, label: 'Jodhpur', state: 'Rajasthan' },
    'udaipur': { lat: 24.5854, lon: 73.7125, label: 'Udaipur', state: 'Rajasthan' },
    'kota': { lat: 25.2138, lon: 75.8648, label: 'Kota', state: 'Rajasthan' },

    // ─── UTTAR PRADESH ───────────────────────────────────────────────────────
    'lucknow': { lat: 26.8467, lon: 80.9462, label: 'Lucknow', state: 'Uttar Pradesh' },
    'kanpur': { lat: 26.4499, lon: 80.3319, label: 'Kanpur', state: 'Uttar Pradesh' },
    'agra': { lat: 27.1767, lon: 78.0081, label: 'Agra', state: 'Uttar Pradesh' },
    'varanasi': { lat: 25.3176, lon: 82.9739, label: 'Varanasi', state: 'Uttar Pradesh' },
    'prayagraj': { lat: 25.4358, lon: 81.8464, label: 'Prayagraj', state: 'Uttar Pradesh' },

    // ─── WEST BENGAL ─────────────────────────────────────────────────────────
    'kolkata': { lat: 22.5726, lon: 88.3639, label: 'Kolkata', state: 'West Bengal' },
    'calcutta': { lat: 22.5726, lon: 88.3639, label: 'Kolkata', state: 'West Bengal' },
    'howrah': { lat: 22.5958, lon: 88.2636, label: 'Howrah', state: 'West Bengal' },

    // ─── PUNJAB / HARYANA / HIMACHAL ─────────────────────────────────────────
    'chandigarh': { lat: 30.7333, lon: 76.7794, label: 'Chandigarh', state: 'Chandigarh' },
    'ludhiana': { lat: 30.9010, lon: 75.8573, label: 'Ludhiana', state: 'Punjab' },
    'amritsar': { lat: 31.6340, lon: 74.8723, label: 'Amritsar', state: 'Punjab' },
    'shimla': { lat: 31.1048, lon: 77.1734, label: 'Shimla', state: 'Himachal Pradesh' },

    // ─── MADHYA PRADESH ──────────────────────────────────────────────────────
    'bhopal': { lat: 23.2599, lon: 77.4126, label: 'Bhopal', state: 'Madhya Pradesh' },
    'indore': { lat: 22.7196, lon: 75.8577, label: 'Indore', state: 'Madhya Pradesh' },
    'jabalpur': { lat: 23.1815, lon: 79.9864, label: 'Jabalpur', state: 'Madhya Pradesh' },
    'gwalior': { lat: 26.2183, lon: 78.1828, label: 'Gwalior', state: 'Madhya Pradesh' },

    // ─── BIHAR / JHARKHAND ────────────────────────────────────────────────────
    'patna': { lat: 25.5941, lon: 85.1376, label: 'Patna', state: 'Bihar' },
    'ranchi': { lat: 23.3441, lon: 85.3096, label: 'Ranchi', state: 'Jharkhand' },
    'jamshedpur': { lat: 22.8046, lon: 86.2029, label: 'Jamshedpur', state: 'Jharkhand' },

    // ─── ODISHA ──────────────────────────────────────────────────────────────
    'bhubaneswar': { lat: 20.2961, lon: 85.8245, label: 'Bhubaneswar', state: 'Odisha' },

    // ─── ASSAM / NORTH EAST ───────────────────────────────────────────────────
    'guwahati': { lat: 26.1445, lon: 91.7362, label: 'Guwahati', state: 'Assam' },
};
